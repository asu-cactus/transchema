import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

df0['Publisher'] = df0['Publisher'].astype(str)
grouped = df0.groupby('Publisher', dropna=False).agg({'name':'count'}).reset_index()
grouped.columns = ['Publisher', 'Publisher_count']
grouped['Publisher'] = pd.to_numeric(grouped['Publisher'], errors='coerce')

result = grouped[['Publisher']].copy()
result = result.dropna(subset=['Publisher'])
result['Publisher'] = result['Publisher'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)