import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_93/training_1.csv", index_col=0)

df0_agg = df0.groupby(['Mouse ID', 'Timepoint'], as_index=False).agg({
    'Tumor Volume (mm3)': ['mean', 'max'],
    'Metastatic Sites': 'sum'
})
df0_agg.columns = ['Mouse ID', 'Timepoint', 'Tumor Volume (mm3)_avg', 'Tumor Volume (mm3)_max', 'Metastatic Sites_sum']

merged = pd.merge(df0_agg, df1, on='Mouse ID', how='inner')

result = merged[['Drug', 'Timepoint', 'Mouse ID']]

result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(str)
result['Drug'] = result['Drug'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_93/target_multisource_mcts.csv", index=False)