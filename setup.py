from setuptools import setup, find_packages

setup(
    name='qiime2_blankremoval_plugin',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
    'qiime2.plugins': ['qiime2_blankremoval_plugin = qiime2_blankremoval_plugin.plugin_setup:plugin']
    },
    author='Your Name',
    author_email='your@email.com',
    description='A QIIME 2 plugin for dummy functions.',
    license='Your License',
    url='https://github.com/pluckySquid/qiime2_blank_removal_plugin.git',
    install_requires=[
        'qiime2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Your License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
)
