import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_55/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_df = pd.concat(dfs, ignore_index=True)

agg_df = union_df.groupby('revol_util', as_index=False).size()
agg_df.rename(columns={'size': 'revol_util'}, inplace=True)
agg_df = agg_df.rename(columns={'revol_util': 'count'})
# The target schema expects 'revol_util' as integer column with counts as values.
# But target schema is ['revol_util': integer] and target examples show counts as values in revol_util column.
# So we must rename the count column to 'revol_util' to match target schema.

agg_df = agg_df.rename(columns={'count': 'revol_util'})
agg_df['revol_util'] = agg_df['revol_util'].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_55/target_multisource_mcts.csv", index=False)