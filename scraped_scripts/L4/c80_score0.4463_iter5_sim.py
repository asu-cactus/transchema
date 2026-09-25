import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv", index_col=0)

grouped = df0.groupby(['Mouse ID', 'Timepoint']).agg(
    **{
        'Mean of Tumor Volume (mm3)': ('Tumor Volume (mm3)', 'mean'),
        'SEM of Tumor Volume (mm3)': ('Tumor Volume (mm3)', lambda x: x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0),
        'Metastatic Sites': ('Metastatic Sites', 'max')
    }
).reset_index()

merged = pd.merge(grouped, df1, on='Mouse ID', how='left')

result = merged[['Drug', 'Timepoint', 'Mean of Tumor Volume (mm3)', 'Mouse ID', 'SEM of Tumor Volume (mm3)', 'Metastatic Sites']]

result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(str)
result['Drug'] = result['Drug'].astype(str)
result['Mean of Tumor Volume (mm3)'] = result['Mean of Tumor Volume (mm3)'].astype(float)
result['SEM of Tumor Volume (mm3)'] = result['SEM of Tumor Volume (mm3)'].astype(float)
result['Metastatic Sites'] = result['Metastatic Sites'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv", index=False)