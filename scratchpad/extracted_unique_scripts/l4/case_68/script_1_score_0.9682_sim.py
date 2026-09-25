import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

agg0 = df0.groupby('school_name').agg({'type': 'first', 'size': 'sum', 'budget': 'sum'}).reset_index()

agg1 = df1.groupby('school_name').agg({'reading_score': 'mean', 'math_score': 'mean'}).reset_index()

merged = pd.merge(agg0, agg1, on='school_name', how='inner')

merged['a'] = merged['type']
merged['b'] = merged['size'].astype(int)
merged['c'] = merged['budget'].astype(int)
merged['d'] = merged['reading_score']
merged['e'] = merged['math_score']

result = merged[['school_name', 'a', 'b', 'c', 'd', 'e']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)