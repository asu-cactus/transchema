import pandas as pd

src_paths = {
    "Source9_99_0": "autopipeline-benchmarks/github-pipelines/length9_99/training_0.csv",
    "Source9_99_1": "autopipeline-benchmarks/github-pipelines/length9_99/training_1.csv",
    "Source9_99_2": "autopipeline-benchmarks/github-pipelines/length9_99/training_2.csv",
    "Source9_99_3": "autopipeline-benchmarks/github-pipelines/length9_99/training_3.csv",
    "Source9_99_4": "autopipeline-benchmarks/github-pipelines/length9_99/training_4.csv",
    "Source9_99_5": "autopipeline-benchmarks/github-pipelines/length9_99/training_5.csv",
    "Source9_99_6": "autopipeline-benchmarks/github-pipelines/length9_99/training_6.csv",
    "Source9_99_7": "autopipeline-benchmarks/github-pipelines/length9_99/training_7.csv",
    "Source9_99_8": "autopipeline-benchmarks/github-pipelines/length9_99/training_8.csv",
    "Source9_99_9": "autopipeline-benchmarks/github-pipelines/length9_99/training_9.csv",
}

df_0 = pd.read_csv(src_paths["Source9_99_0"], index_col=0)
df_4 = pd.read_csv(src_paths["Source9_99_4"], index_col=0)

join_cols = ['admit', 'gre', 'gpa', 'prestige']
df_joined = pd.merge(df_0, df_4, left_on=join_cols, right_on=join_cols, how='inner', suffixes=('_0', '_4'))

sources_to_union = [
    "Source9_99_0", "Source9_99_1", "Source9_99_2", "Source9_99_3",
    "Source9_99_5", "Source9_99_6", "Source9_99_7", "Source9_99_8", "Source9_99_9"
]

dfs_union = [pd.read_csv(src_paths[src], index_col=0) for src in sources_to_union]
df_union = pd.concat(dfs_union, ignore_index=True)

df_union = df_union.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

df_union.to_csv("autopipeline-benchmarks/github-pipelines/length9_99/target_multisource_mcts.csv", index=False)