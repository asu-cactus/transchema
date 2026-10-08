import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_3.csv", index_col=0)

j01 = pd.merge(s0, s1, on="WarNum", suffixes=('_0', '_1'))
j012 = pd.merge(j01, s2, on="WarNum")
j0123 = pd.merge(j012, s3, on="WarNum", suffixes=('', '_3'))

# After joins, we have multiple TransTo columns: TransTo_0, TransTo_1, TransTo, TransTo_3
# We need to produce a single TransTo column for grouping.
# Since all TransTo columns are mostly NaN, but target examples show TransTo with integer values,
# we take the first non-null TransTo value per row from these columns.

trans_cols = ['TransTo_0', 'TransTo_1', 'TransTo', 'TransTo_3']
j0123['TransTo'] = j0123[trans_cols].bfill(axis=1).iloc[:, 0]

result = j0123[['TransTo', 'WarNum']].copy()
result = result.dropna(subset=['TransTo', 'WarNum'])
result['TransTo'] = result['TransTo'].astype(int)
result['WarNum'] = result['WarNum'].astype(int)

result = result.groupby('TransTo', as_index=False).agg({'WarNum':'first'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_57/target_multisource_mcts.csv", index=False)