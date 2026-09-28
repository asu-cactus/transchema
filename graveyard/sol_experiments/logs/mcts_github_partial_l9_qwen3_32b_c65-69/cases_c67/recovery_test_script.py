import pandas as pd

# Load dimension tables and union them
dfs = []
for i in [2,3,4,9]:
    src = f'autopipeline-benchmarks/github-pipelines/length9_67/training_{i}.csv'
    dfs.append(pd.read_csv(src, index_col=0))
core = pd.concat(dfs, axis=0).reset_index(drop=True)

# Group by leftmost unique columns to eliminate duplicates
core = core.groupby(['CANCELED', 'ROW_WID'], as_index=False).first()

# Join with aspect tables containing numerical attributes
src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/test_0.csv', index_col=0)
core = core.merge(src0, on='ROW_WID', how='left')

src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/test_1.csv', index_col=0)
core = core.merge(src1, on='ROW_WID', how='left')

src5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/test_5.csv', index_col=0)
core = core.merge(src5, on='ROW_WID', how='left')

src6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/test_6.csv', index_col=0)
core = core.merge(src6, on='ROW_WID', how='left')

src7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/test_7.csv', index_col=0)
core = core.merge(src7, on='ROW_WID', how='left')

src8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/test_8.csv', index_col=0)
core = core.merge(src8, on='ROW_WID', how='left')

# Write final output
core.to_csv('autopipeline-benchmarks/github-pipelines/length9_67/target_multisource_mcts_recovery_test_val.csv', index=False)