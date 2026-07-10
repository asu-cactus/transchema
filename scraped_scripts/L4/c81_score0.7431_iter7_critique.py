import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

df_merged = pd.merge(df0, df1, on="Mouse ID")

grouped = df_merged.groupby(['Drug', 'Timepoint'], as_index=False).agg(
    {
        'Metastatic Sites': ['mean', 'sem'],
        'Tumor Volume (mm3)': 'mean',
        'Mouse ID': 'count'
    }
)

# Flatten MultiIndex columns
grouped.columns = [
    'Drug',
    'Timepoint',
    'Mean of Metastatic Sites',
    'SEM of Metastatic Sites',
    'Tumor Volume (mm3)',
    'Mouse ID'
]

# Reorder columns to match target schema: ['Drug', 'Timepoint', 'Mean of Metastatic Sites', 'Mouse ID', 'Tumor Volume (mm3)', 'SEM of Metastatic Sites']
grouped = grouped[['Drug', 'Timepoint', 'Mean of Metastatic Sites', 'Mouse ID', 'Tumor Volume (mm3)', 'SEM of Metastatic Sites']]

grouped['Timepoint'] = grouped['Timepoint'].astype(int)
grouped['Mean of Metastatic Sites'] = grouped['Mean of Metastatic Sites'].astype(float)
grouped['Mouse ID'] = grouped['Mouse ID'].astype(int)
grouped['Tumor Volume (mm3)'] = grouped['Tumor Volume (mm3)'].round().astype(int)
grouped['SEM of Metastatic Sites'] = grouped['SEM of Metastatic Sites'].fillna(0).round().astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)