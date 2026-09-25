import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_66/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_66/training_1.csv", index_col=0)

merged = pd.merge(df1, df0[['school_name']], on='school_name')

result = merged.groupby('school_name', as_index=False)['reading_score'].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_66/target_multisource_mcts.csv", index=False)