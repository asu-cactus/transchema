import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_2.csv", index_col=0)

df = pd.DataFrame()
df['key'] = s0['0']
df['count'] = 1
df['max_s1'] = s1['0']
df['min_s2'] = s2['0']

agg = df.groupby('key').agg({'count':'count', 'max_s1':'max', 'min_s2':'min'}).reset_index()

result = agg[['count']].rename(columns={'count':'0'})
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_39/target_multisource_mcts.csv", index=False)