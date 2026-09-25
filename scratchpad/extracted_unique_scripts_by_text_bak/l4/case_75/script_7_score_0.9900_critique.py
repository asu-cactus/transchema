import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_1.csv", index_col=0)

merged = pd.merge(df1, df0[['school_name', 'type']], on='school_name', how='inner')

result = merged.groupby('type').agg(a=('reading_score', 'mean'), b=('math_score', 'mean')).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts.csv", index=False)