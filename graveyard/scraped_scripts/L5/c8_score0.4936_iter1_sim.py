import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_8/training_1.csv", index_col=0)

merged = pd.merge(df1[['school_name']], df0[['school_name', 'math_score']], on='school_name')

result = merged[['school_name', 'math_score']].copy()
result['math_score'] = result['math_score'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_8/target_multisource_mcts.csv", index=False)