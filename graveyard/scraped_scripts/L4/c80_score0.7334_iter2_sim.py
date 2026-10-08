import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID")

grouped = merged.groupby(['Drug', 'Timepoint']).agg(
    Mean_of_Tumor_Volume_mm3 = ('Tumor Volume (mm3)', 'mean'),
    SEM_of_Tumor_Volume_mm3 = ('Tumor Volume (mm3)', lambda x: x.std(ddof=1) / np.sqrt(len(x))),
    Mean_of_Metastatic_Sites = ('Metastatic Sites', 'mean'),
    Mouse_ID_Count = ('Mouse ID', 'count')
).reset_index()

grouped['Mouse ID'] = grouped['Mouse_ID_Count'].astype(int)
grouped['Timepoint'] = grouped['Timepoint'].astype(int)
grouped['Mean_of_Tumor_Volume_mm3'] = grouped['Mean_of_Tumor_Volume_mm3'].astype(float)
grouped['SEM_of_Tumor_Volume_mm3'] = grouped['SEM_of_Tumor_Volume_mm3'].astype(float)
grouped['Mean_of_Metastatic_Sites'] = grouped['Mean_of_Metastatic_Sites'].astype(float)

result = grouped.rename(columns={
    'Mean_of_Tumor_Volume_mm3': 'Mean of Tumor Volume (mm3)',
    'SEM_of_Tumor_Volume_mm3': 'SEM of Tumor Volume (mm3)',
    'Mean_of_Metastatic_Sites': 'Metastatic Sites'
})

result = result[['Drug', 'Timepoint', 'Mean of Tumor Volume (mm3)', 'Mouse ID', 'SEM of Tumor Volume (mm3)', 'Metastatic Sites']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv", index=False)