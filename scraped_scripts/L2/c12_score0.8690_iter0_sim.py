import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_12/training_1.csv", index_col=0)

merged = pd.merge(df1, df0[['school_name', 'size']], on='school_name')

result = merged.groupby('school_name', as_index=False)['size'].sum()
result = result.rename(columns={'size': 'reading_score'})
result['reading_score'] = result['reading_score'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_12/target_multisource_mcts.csv", index=False)