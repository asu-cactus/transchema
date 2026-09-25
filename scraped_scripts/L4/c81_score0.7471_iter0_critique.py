import pandas as pd
import numpy as np

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv', index_col=0)

# Join on Mouse ID as string (no conversion)
df_join = pd.merge(df0, df1, on='Mouse ID', how='inner')

# Group by Drug and Timepoint
grouped = df_join.groupby(['Drug', 'Timepoint'])

# Aggregations
mean_met = grouped['Metastatic Sites'].mean()
sem_met = grouped['Metastatic Sites'].sem().fillna(0)
count_mouse = grouped['Mouse ID'].nunique()
mean_tumor = grouped['Tumor Volume (mm3)'].mean()

# Build result DataFrame
result = pd.DataFrame({
    'Drug': mean_met.index.get_level_values('Drug'),
    'Timepoint': mean_met.index.get_level_values('Timepoint'),
    'Mean of Metastatic Sites': mean_met.values,
    'Mouse ID': count_mouse.values,
    'Tumor Volume (mm3)': mean_tumor.values,
    'SEM of Metastatic Sites': sem_met.values
})

# Cast columns to target types
result['Drug'] = result['Drug'].astype(str)
result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(int)
result['Tumor Volume (mm3)'] = result['Tumor Volume (mm3)'].round().astype(int)
result['Mean of Metastatic Sites'] = result['Mean of Metastatic Sites'].astype(float)
result['SEM of Metastatic Sites'] = result['SEM of Metastatic Sites'].round().astype(int)

result.to_csv('autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv', index=False)