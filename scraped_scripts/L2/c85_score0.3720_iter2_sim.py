import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_85/training_1.csv", index_col=0)

grouped_0 = df0.groupby(['Mouse ID', 'Timepoint'], as_index=False).agg({
    'Tumor Volume (mm3)': 'mean',
    'Metastatic Sites': 'sum'
})

merged = pd.merge(grouped_0, df1, on='Mouse ID', how='inner')

result = merged[['Drug', 'Timepoint', 'Mouse ID']]

result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(str)
result['Drug'] = result['Drug'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_85/target_multisource_mcts.csv", index=False)