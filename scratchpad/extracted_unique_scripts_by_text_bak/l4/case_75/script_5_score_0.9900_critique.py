import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_1.csv", index_col=0)

# Join on school_name to get type for each student
df_joined = pd.merge(df1, df0[['school_name', 'type']], on='school_name', how='inner')

# Group by type and aggregate average reading and math scores
result = df_joined.groupby('type').agg(a=('reading_score', 'mean'), b=('math_score', 'mean')).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts.csv", index=False)