import pandas as pd
import numpy as np

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

# Join on Mouse ID
merged = pd.merge(source0, source1, on="Mouse ID", how="inner")

# Group by Drug and Timepoint
grouped = merged.groupby(['Drug', 'Timepoint'])

# Aggregations:
# Mean of Metastatic Sites
mean_met_sites = grouped['Metastatic Sites'].mean()

# SEM of Metastatic Sites = std / sqrt(n)
sem_met_sites = grouped['Metastatic Sites'].sem()

# Count distinct Mouse ID per group (Mouse ID is string, count unique)
count_mouse_id = grouped['Mouse ID'].nunique()

# Mean Tumor Volume (mm3)
mean_tumor_vol = grouped['Tumor Volume (mm3)'].mean()

# Compose final DataFrame
result = pd.DataFrame({
    'Drug': mean_met_sites.index.get_level_values('Drug'),
    'Timepoint': mean_met_sites.index.get_level_values('Timepoint'),
    'Mean of Metastatic Sites': mean_met_sites.values,
    'Mouse ID': count_mouse_id.values,
    'Tumor Volume (mm3)': mean_tumor_vol.values,
    'SEM of Metastatic Sites': sem_met_sites.values
})

# Convert types to match target schema
result['Drug'] = result['Drug'].astype(str)
result['Timepoint'] = result['Timepoint'].astype(int)
result['Mean of Metastatic Sites'] = result['Mean of Metastatic Sites'].astype(float)
result['Mouse ID'] = result['Mouse ID'].astype(int)
result['Tumor Volume (mm3)'] = result['Tumor Volume (mm3)'].round().astype(int)
result['SEM of Metastatic Sites'] = result['SEM of Metastatic Sites'].round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)