import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_1.csv", index_col=0)

agg = df0.groupby('Mouse ID').agg({
    'Tumor Volume (mm3)': 'min',
    'Metastatic Sites': 'sum',
    'Timepoint': 'count'
}).reset_index()

joined = pd.merge(agg, df1, on='Mouse ID', how='inner')

result = joined[['Drug', 'Timepoint', 'Mouse ID']]

result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(str)
result['Drug'] = result['Drug'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_51/target_multisource_mcts.csv", index=False)