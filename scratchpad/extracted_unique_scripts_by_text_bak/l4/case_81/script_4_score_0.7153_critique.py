import pandas as pd
import numpy as np

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

# Join on Mouse ID
merged = pd.merge(source0, source1, on='Mouse ID', how='inner')

# Group by Drug and Timepoint
grouped = merged.groupby(['Drug', 'Timepoint']).agg(
    mean_metastatic_sites=('Metastatic Sites', 'mean'),
    mean_tumor_volume=('Tumor Volume (mm3)', 'mean'),
    mouse_id_count=('Mouse ID', pd.Series.nunique),
    std_metastatic_sites=('Metastatic Sites', 'std'),
    count_metastatic_sites=('Metastatic Sites', 'count')
).reset_index()

# Calculate SEM of Metastatic Sites
grouped['sem_metastatic_sites'] = grouped['std_metastatic_sites'] / np.sqrt(grouped['count_metastatic_sites'])
grouped['sem_metastatic_sites'] = grouped['sem_metastatic_sites'].fillna(0)

# Prepare final result with correct column names and types
result = pd.DataFrame()
result['Drug'] = grouped['Drug'].astype(str)
result['Timepoint'] = grouped['Timepoint'].astype(int)
result['Mean of Metastatic Sites'] = grouped['mean_metastatic_sites'].astype(float)
result['Mouse ID'] = grouped['mouse_id_count'].astype(int)
result['Tumor Volume (mm3)'] = grouped['mean_tumor_volume'].round().astype(int)
result['SEM of Metastatic Sites'] = grouped['sem_metastatic_sites'].round().astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)