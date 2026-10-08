import pandas as pd
import numpy as np

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv', index_col=0)

df_join = pd.merge(df0, df1, on='Mouse ID', how='inner')

df_join['Mouse ID'] = pd.to_numeric(df_join['Mouse ID'], errors='coerce')

grouped = df_join.groupby(['Drug', 'Timepoint', 'Mouse ID', 'Tumor Volume (mm3)'])['Metastatic Sites']
mean_met = grouped.mean()
sem_met = grouped.sem()

result = pd.DataFrame({
    'Drug': mean_met.index.get_level_values('Drug'),
    'Timepoint': mean_met.index.get_level_values('Timepoint'),
    'Mouse ID': mean_met.index.get_level_values('Mouse ID'),
    'Tumor Volume (mm3)': mean_met.index.get_level_values('Tumor Volume (mm3)'),
    'Mean of Metastatic Sites': mean_met.values,
    'SEM of Metastatic Sites': sem_met.values
})

result['Drug'] = result['Drug'].astype(str)
result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(int)
result['Tumor Volume (mm3)'] = result['Tumor Volume (mm3)'].round().astype(int)
result['Mean of Metastatic Sites'] = result['Mean of Metastatic Sites'].astype(float)
result['SEM of Metastatic Sites'] = result['SEM of Metastatic Sites'].fillna(0).round().astype(int)

result.to_csv('autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv', index=False)