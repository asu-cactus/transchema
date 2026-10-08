import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

# Join on Mouse ID to get Drug info for each measurement
merged = pd.merge(df0, df1, on='Mouse ID', how='inner')

# Define a function to compute SEM
def sem(x):
    return x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0

# Group by Drug and Timepoint (leftmost non-float columns in target)
grouped = merged.groupby(['Drug', 'Timepoint']).agg(
    **{
        'Mean of Metastatic Sites': ('Metastatic Sites', 'mean'),
        'SEM of Metastatic Sites': ('Metastatic Sites', sem),
        'Mouse ID': ('Mouse ID', pd.Series.nunique),
        'Tumor Volume (mm3)': ('Tumor Volume (mm3)', 'mean')
    }
).reset_index()

# Convert types to match target schema
grouped['Timepoint'] = grouped['Timepoint'].astype(int)
grouped['Mouse ID'] = grouped['Mouse ID'].astype(int)
grouped['Mean of Metastatic Sites'] = grouped['Mean of Metastatic Sites'].astype(float)
grouped['SEM of Metastatic Sites'] = grouped['SEM of Metastatic Sites'].astype(float)
grouped['Tumor Volume (mm3)'] = grouped['Tumor Volume (mm3)'].round().astype(int)
grouped['Drug'] = grouped['Drug'].astype(str)

# Reorder columns to match target schema
result = grouped[['Drug', 'Timepoint', 'Mean of Metastatic Sites', 'Mouse ID', 'Tumor Volume (mm3)', 'SEM of Metastatic Sites']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)