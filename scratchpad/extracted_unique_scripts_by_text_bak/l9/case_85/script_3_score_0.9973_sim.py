import pandas as pd

src_paths = {
    "Source9_85_0": "autopipeline-benchmarks/github-pipelines/length9_85/training_0.csv",
    "Source9_85_1": "autopipeline-benchmarks/github-pipelines/length9_85/training_1.csv",
    "Source9_85_2": "autopipeline-benchmarks/github-pipelines/length9_85/training_2.csv",
    "Source9_85_3": "autopipeline-benchmarks/github-pipelines/length9_85/training_3.csv",
    "Source9_85_4": "autopipeline-benchmarks/github-pipelines/length9_85/training_4.csv",
    "Source9_85_5": "autopipeline-benchmarks/github-pipelines/length9_85/training_5.csv",
    "Source9_85_6": "autopipeline-benchmarks/github-pipelines/length9_85/training_6.csv",
    "Source9_85_7": "autopipeline-benchmarks/github-pipelines/length9_85/training_7.csv",
    "Source9_85_8": "autopipeline-benchmarks/github-pipelines/length9_85/training_8.csv",
    "Source9_85_9": "autopipeline-benchmarks/github-pipelines/length9_85/training_9.csv",
}

df_0 = pd.read_csv(src_paths["Source9_85_0"], index_col=0)
df_5 = pd.read_csv(src_paths["Source9_85_5"], index_col=0)

join_cols = ['admit', 'gre', 'gpa', 'prestige']
df_joined = pd.merge(df_0, df_5, on=join_cols, how='inner')

union_sources = [
    "Source9_85_0", "Source9_85_1", "Source9_85_2", "Source9_85_3", "Source9_85_4",
    "Source9_85_6", "Source9_85_7", "Source9_85_8", "Source9_85_9"
]

dfs_union = [pd.read_csv(src_paths[src], index_col=0) for src in union_sources]
df_union = pd.concat(dfs_union, ignore_index=True)

df_final = pd.concat([df_joined, df_union], ignore_index=True)

df_final = df_final.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_85/target_multisource_mcts.csv", index=False)