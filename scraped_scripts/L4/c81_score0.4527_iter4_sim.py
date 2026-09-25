import pandas as pd
import numpy as np

def sem(x):
    return x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0.0

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

grouped = source1.groupby(['Mouse ID', 'Timepoint']).agg(
    Tumor_Volume_Mean=('Tumor Volume (mm3)', 'mean'),
    Metastatic_Sites_Mean=('Metastatic Sites', 'mean'),
    Metastatic_Sites_SEM=('Metastatic Sites', sem)
).reset_index()

merged = pd.merge(grouped, source0, on='Mouse ID', how='inner')

result = merged.rename(columns={
    'Tumor_Volume_Mean': 'Tumor Volume (mm3)',
    'Metastatic_Sites_Mean': 'Mean of Metastatic Sites',
    'Metastatic_Sites_SEM': 'SEM of Metastatic Sites'
})

result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(str)
result['Drug'] = result['Drug'].astype(str)
result['Mean of Metastatic Sites'] = result['Mean of Metastatic Sites'].astype(float)
result['Tumor Volume (mm3)'] = result['Tumor Volume (mm3)'].round().astype(int)
result['SEM of Metastatic Sites'] = result['SEM of Metastatic Sites'].round().astype(int)

result = result[['Drug', 'Timepoint', 'Mean of Metastatic Sites', 'Mouse ID', 'Tumor Volume (mm3)', 'SEM of Metastatic Sites']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)