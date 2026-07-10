import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_12/training_1.csv", index_col=0)

df0_subset = df0[['school_name', 'size']].rename(columns={'size': 'reading_score'})
df1_subset = df1[['school_name', 'reading_score']]

df_union = pd.concat([df0_subset, df1_subset], ignore_index=True)

result = df_union.groupby('school_name', as_index=False)['reading_score'].sum()
result['reading_score'] = result['reading_score'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_12/target_multisource_mcts.csv", index=False)