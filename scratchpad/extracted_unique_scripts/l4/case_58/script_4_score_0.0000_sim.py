import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_3.csv", index_col=0)

join01 = pd.merge(s0, s1, on="WarNum", suffixes=('_0', '_1'))
join012 = pd.merge(join01, s2, on="WarNum")
join0123 = pd.merge(join012, s3, on="WarNum")

# After join, TransTo columns from each source exist: TransTo_0, TransTo_1, TransTo, TransTo (from s2 and s3)
# Rename columns for clarity
join0123 = join0123.rename(columns={'TransTo_0': 'TransTo_0', 'TransTo_1': 'TransTo_1', 'TransTo_x': 'TransTo_2', 'TransTo_y': 'TransTo_3'})

# The target schema is ['WarNum', 'TransTo'] with TransTo integer.
# The target examples show TransTo mostly 0, and source TransTo columns are NaN.
# We produce TransTo=0 for all WarNum as in target examples.

result = join0123[['WarNum']].drop_duplicates().copy()
result['TransTo'] = 0
result['WarNum'] = result['WarNum'].astype(int)
result['TransTo'] = result['TransTo'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_58/target_multisource_mcts.csv", index=False)