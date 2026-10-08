import pandas as pd
import numpy as np

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

grouped = source1.groupby(['Mouse ID', 'Timepoint']).agg(
    mean_metastatic_sites=('Metastatic Sites', 'mean'),
    mean_tumor_volume=('Tumor Volume (mm3)', 'mean'),
    count_metastatic_sites=('Metastatic Sites', 'count'),
    std_metastatic_sites=('Metastatic Sites', 'std')
).reset_index()

grouped['sem_metastatic_sites'] = grouped['std_metastatic_sites'] / np.sqrt(grouped['count_metastatic_sites'])
grouped['sem_metastatic_sites'] = grouped['sem_metastatic_sites'].fillna(0)

merged = pd.merge(grouped, source0, on='Mouse ID', how='inner')

result = pd.DataFrame()
result['Drug'] = merged['Drug'].astype(str)
result['Timepoint'] = merged['Timepoint'].astype(int)
result['Mean of Metastatic Sites'] = merged['mean_metastatic_sites'].astype(float)
result['Mouse ID'] = merged['Mouse ID'].astype(int, errors='ignore')
result['Tumor Volume (mm3)'] = merged['mean_tumor_volume'].round().astype(int)
result['SEM of Metastatic Sites'] = merged['sem_metastatic_sites'].round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)