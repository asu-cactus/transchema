import pandas as pd
import numpy as np

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv', index_col=0)

df_merged = pd.merge(df0, df1, on='Mouse ID')

agg = df_merged.groupby(['Drug', 'Timepoint', 'Mouse ID', 'Tumor Volume (mm3)'])['Metastatic Sites'].agg(['mean', 'sem']).reset_index()

agg = agg.rename(columns={'mean': 'Mean of Metastatic Sites', 'sem': 'SEM of Metastatic Sites'})

agg['Timepoint'] = agg['Timepoint'].astype(int)
agg['Mouse ID'] = agg['Mouse ID'].astype(str)
agg['Drug'] = agg['Drug'].astype(str)
agg['Tumor Volume (mm3)'] = agg['Tumor Volume (mm3)'].astype(int)
agg['SEM of Metastatic Sites'] = agg['SEM of Metastatic Sites'].fillna(0).astype(int)

agg.to_csv('autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv', index=False)