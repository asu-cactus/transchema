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

df_all = pd.concat(dfs, ignore_index=True)

df_grouped = df_all.groupby('revol_util', as_index=False).size()

df_grouped.rename(columns={'size': 'revol_util'}, inplace=True)

# The target schema is ['revol_util': integer], and target examples show values like 2,7,1
# The groupby size counts occurrences, but target schema expects revol_util as integer values, not counts.
# So the groupby is just to get unique revol_util values, not counts.
# We should just get unique revol_util values as integers.

df_result = pd.DataFrame({'revol_util': df_all['revol_util'].astype(int).unique()})
df_result = df_result.sort_values('revol_util').reset_index(drop=True)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_55/target_multisource_mcts.csv", index=False)