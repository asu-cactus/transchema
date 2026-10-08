import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_20/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_20/training_1.csv", index_col=0)

agg = df0.groupby(['Timepoint', 'Mouse ID'], as_index=False).agg({
    'Tumor Volume (mm3)': ['mean', 'max'],
    'Metastatic Sites': 'sum'
})
agg.columns = ['Timepoint', 'Mouse ID', 'Tumor Volume (mm3)_mean', 'Tumor Volume (mm3)_max', 'Metastatic Sites_sum']

merged = pd.merge(agg, df1, on='Mouse ID', how='inner')

result = merged[['Drug', 'Timepoint', 'Mouse ID']]

result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(int, errors='ignore')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_20/target_multisource_mcts.csv", index=False)