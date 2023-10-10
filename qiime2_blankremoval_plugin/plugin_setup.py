import qiime2
import biom
import qiime2.plugin
import pandas as pd
from q2_types.feature_table import FeatureTable, RelativeFrequency, Frequency


def blankremoval_function(input_artifact: biom.Table) -> biom.Table:

    # When cutoff is low, more noise (or background) detected; With higher cutoff, less background detected, thus more features observed
    cutoff = 0.1

    #condition = "SD_01-2018+5_b.mzXML"

    df = input_artifact.to_dataframe(dense=True)

    md = pd.read_csv("data/metadata.tsv", sep = "\t").set_index("sample id")
    new_md = md.copy()
    new_ft = df.copy() 

    if sorted(new_ft.columns) != sorted(new_md.index):
        # print the md rows / ft column which are not in ft columns / md rows and remove them
        ft_cols_not_in_md = [col for col in new_ft.columns if col not in new_md.index]
        new_ft.drop(columns=ft_cols_not_in_md, inplace=True)
        md_rows_not_in_ft = [row for row in new_md.index if row not in new_ft.columns]
        new_md.drop(md_rows_not_in_ft, inplace=True)

       # Convert the input biom table to a pandas DataFrame
    df = input_artifact.to_dataframe()

    new_ft = new_ft.reindex(sorted(new_ft.columns), axis=1)

    # Convert the filtered DataFrame back to a biom table
    table_filtered = biom.Table(new_ft.values, observation_ids=new_ft.index, sample_ids=new_ft.columns)


    return table_filtered

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
    parameters={},  # Add parameters if necessary
    outputs=[('output_artifact', FeatureTable[RelativeFrequency])],
    output_descriptions={
        'output_artifact': 'Description of the output artifact.'
    },
    name='dummy-function',
    description='A description of your function.',
)