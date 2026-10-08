import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_1.csv", index_col=0)

agg = df2.groupby(['city', 'type'], as_index=False)['driver_count'].sum()

agg['type'] = agg['type'].astype(str)
agg['type'] = agg['type'].apply(lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else 0)

agg[['city', 'type']].to_csv("autopipeline-benchmarks/github-pipelines/length2_23/target_multisource_mcts.csv", index=False)