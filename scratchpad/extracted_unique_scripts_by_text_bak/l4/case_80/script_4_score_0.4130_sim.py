import pandas as pd
import numpy as np

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv', index_col=0)

df = pd.merge(df0, df1, on='Mouse ID', how='inner')

df['Mouse ID int'] = pd.factorize(df['Mouse ID'])[0] + 1

grouped = df.groupby(['Drug', 'Timepoint', 'Mouse ID int'])

mean_tumor = grouped['Tumor Volume (mm3)'].mean()
std_tumor = grouped['Tumor Volume (mm3)'].std()
count = grouped['Tumor Volume (mm3)'].count()
sem_tumor = std_tumor / np.sqrt(count)
sem_tumor = sem_tumor.fillna(0)

metastatic_sites = grouped['Metastatic Sites'].first()

result = pd.DataFrame({
    'Drug': mean_tumor.index.get_level_values('Drug'),
    'Timepoint': mean_tumor.index.get_level_values('Timepoint').astype(int),
    'Mean of Tumor Volume (mm3)': mean_tumor.values,
    'Mouse ID': mean_tumor.index.get_level_values('Mouse ID int').astype(int),
    'SEM of Tumor Volume (mm3)': sem_tumor.round().astype(int),
    'Metastatic Sites': metastatic_sites.astype(int)
})

result.to_csv('autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv', index=False)