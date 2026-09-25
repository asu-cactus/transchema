import pandas as pd
import numpy as np

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

grouped = source1.groupby(['Mouse ID', 'Timepoint'], as_index=False).agg({
    'Tumor Volume (mm3)': 'sum',
    'Metastatic Sites': ['sum', 'count']
})
grouped.columns = ['Mouse ID', 'Timepoint', 'Tumor Volume (mm3)', 'Sum Metastatic Sites', 'Count Metastatic Sites']

joined = pd.merge(grouped, source0, on='Mouse ID', how='inner')

joined['Mean of Metastatic Sites'] = joined['Sum Metastatic Sites'] / joined['Count Metastatic Sites']
joined['SEM of Metastatic Sites'] = 0

joined['Drug'] = joined['Drug'].astype(str)
joined['Timepoint'] = joined['Timepoint'].astype(int)
joined['Mean of Metastatic Sites'] = joined['Mean of Metastatic Sites'].astype(float)
joined['Mouse ID'] = joined['Mouse ID'].astype(str)
joined['Tumor Volume (mm3)'] = joined['Tumor Volume (mm3)'].round().astype(int)
joined['SEM of Metastatic Sites'] = joined['SEM of Metastatic Sites'].astype(int)

joined['Mouse ID'] = joined['Mouse ID'].str.extract('(\d+)').astype(int)

result = joined[['Drug', 'Timepoint', 'Mean of Metastatic Sites', 'Mouse ID', 'Tumor Volume (mm3)', 'SEM of Metastatic Sites']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)