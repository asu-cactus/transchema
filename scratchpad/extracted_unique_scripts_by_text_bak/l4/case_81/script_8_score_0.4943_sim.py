import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

grouped = df1.groupby(['Mouse ID', 'Timepoint']).agg(
    **{
        'Mean of Metastatic Sites': ('Metastatic Sites', 'mean'),
        'SEM of Metastatic Sites': ('Metastatic Sites', lambda x: x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0),
        'Tumor Volume (mm3)': ('Tumor Volume (mm3)', 'sum')
    }
).reset_index()

merged = pd.merge(grouped, df0, on='Mouse ID', how='inner')

merged['Timepoint'] = merged['Timepoint'].astype(int)
merged['Mouse ID'] = merged['Mouse ID'].astype(str)
merged['Drug'] = merged['Drug'].astype(str)
merged['Mean of Metastatic Sites'] = merged['Mean of Metastatic Sites'].astype(float)
merged['SEM of Metastatic Sites'] = merged['SEM of Metastatic Sites'].astype(float)
merged['Tumor Volume (mm3)'] = merged['Tumor Volume (mm3)'].astype(int)

result = merged[['Drug', 'Timepoint', 'Mean of Metastatic Sites', 'Mouse ID', 'Tumor Volume (mm3)', 'SEM of Metastatic Sites']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)