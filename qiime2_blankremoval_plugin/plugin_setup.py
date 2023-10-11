import qiime2
import biom
import pandas as pd

import qiime2.plugin
from qiime2.plugin import Metadata, MetadataColumn, Categorical, Numeric, SemanticType
from q2_types.feature_table import FeatureTable, RelativeFrequency, Frequency


def blankremoval_function(input_artifact: biom.Table, metadatafile: int) -> biom.Table:

    # When cutoff is low, more noise (or background) detected; With higher cutoff, less background detected, thus more features observed
    cutoff = 0.1

    condition = 1

    df = input_artifact.to_dataframe(dense=True)

    md = pd.read_csv(metadatafile, sep = "\t").set_index("sample id")
    new_md = md.copy()
    new_md.index = [name.strip() for name in md.index]
    
    
    # for each col in new_md
    # 1) removing the spaces (if any)
    # 2) replace the spaces (in the middle) to underscore
    # 3) converting them all to UPPERCASE
    for col in new_md.columns:
        if new_md[col].dtype == str:
            new_md[col] = [item.strip().replace(" ", "_").upper() for item in new_md[col]]

    new_ft = df.copy() #storing the files under different names to preserve the original files
    

    new_ft.index.name = "CustomIndex"
    # drop all columns that are not mzML or mzXML file names, I may not need this but it won't hurt
    new_ft.drop(columns=[col for col in new_ft.columns if ".mz" not in col], inplace=True)
    # # remove " Peak area" from column names, may not need but won't hurt
    new_ft.rename(columns={col: col.replace(" Peak area", "").strip() for col in new_ft.columns}, inplace=True)
    

    if sorted(new_ft.columns) != sorted(new_md.index):
        # print the md rows / ft column which are not in ft columns / md rows and remove them
        ft_cols_not_in_md = [col for col in new_ft.columns if col not in new_md.index]
        new_ft.drop(columns=ft_cols_not_in_md, inplace=True)
        md_rows_not_in_ft = [row for row in new_md.index if row not in new_ft.columns]
        new_md.drop(md_rows_not_in_ft, inplace=True)
    new_ft = new_ft.reindex(sorted(new_ft.columns), axis=1)
    
    new_md.sort_index(inplace=True) #ordering the md by its row names
    #new_md.to_csv("data/new_md.txt", header=False, index=False)
    list(new_ft.columns) == list(new_md.index)
    data = new_md

    df = pd.DataFrame({"LEVELS": inside_levels(data).iloc[condition-1]["LEVELS"]})
    df.index = [*range(1, len(df)+1)]
    #df.to_csv("../data/df.txt", header=False, index=False)
    #Among the shown levels of an attribute, select the one to remove
    blank_id = 1

        #Splitting the data into blanks and samples based on the metadata
    md_blank = data[data[inside_levels(data)['ATTRIBUTES'][condition]] == df['LEVELS'][blank_id]]
    blank = new_ft[list(md_blank.index)]
    md_samples = data[data[inside_levels(data)['ATTRIBUTES'][condition]] != df['LEVELS'][blank_id]]

    samples = new_ft[list(md_samples.index)]

    blank_removal = samples.copy()
    
    # Getting mean for every feature in blank and Samples
    avg_blank = blank.mean(axis=1, skipna=False) # set skipna = False do not exclude NA/null values when computing the result.
    avg_samples = samples.mean(axis=1, skipna=False)

    # Getting the ratio of blank vs samples
    ratio_blank_samples = (avg_blank+1)/(avg_samples+1)

    # Create an array with boolean values: True (is a real feature, ratio<cutoff) / False (is a blank, background, noise feature, ratio>cutoff)
    is_real_feature = (ratio_blank_samples<cutoff)
    blank_removal = samples[is_real_feature.values]
    imputation_samples = blank_removal.copy()
    
    # Convert the filtered DataFrame back to a biom table
    table_filtered = biom.Table(imputation_samples.values, observation_ids=imputation_samples.index, sample_ids=imputation_samples.columns)
    return table_filtered

def inside_levels(df):
    # get all the columns (equals all attributes) -> will be number of rows
    levels = []
    types = []
    count = []
    for col in df.columns:
        types.append(type(df[col][0]))
        levels.append(sorted(set(df[col].dropna())))
        tmp = df[col].value_counts()
        count.append([tmp[levels[-1][i]] for i in range(len(levels[-1]))])
    return pd.DataFrame({"ATTRIBUTES": df.columns, "LEVELS": levels, "COUNT":count, "TYPES": types}, index=range(1, len(levels)+1))


plugin = qiime2.plugin.Plugin(
    name='blankremoval_plugin',
    version='0.1.0',
    website='https://github.com/pluckySquid/~/qiime2_blankremoval_plugin.git',
    package='qiime2_blankremoval_plugin',
    description='A QIIME 2 plugin for qiime2_blankremoval_plugin functions.',
    short_description='Plugin for qiime2_blankremoval_plugin analysis.',
)

plugin.methods.register_function(
    function=blankremoval_function,
    inputs={'input_artifact': FeatureTable[Frequency]},
    parameters={'metadatafile': qiime2.plugin.Str},  # Add parameters if necessary
    outputs=[('output_artifact', FeatureTable[Frequency])],
    output_descriptions={
        'output_artifact': 'Description of the output artifact.'
    },
    name='dummy-function',
    description='A description of your function.',
)