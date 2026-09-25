import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_86/training_1.csv", index_col=0)

grouped = df0.groupby('fname').size().reset_index(name='row_count')

result = df1[['fname']].drop_duplicates().merge(grouped, on='fname', how='left')

result['row_count'] = result['row_count'].fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_86/target_multisource_mcts.csv", index=False)