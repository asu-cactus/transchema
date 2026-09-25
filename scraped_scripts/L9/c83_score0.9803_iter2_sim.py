import pandas as pd

src_paths = [
    "autopipeline-benchmarks/github-pipelines/length9_83/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_9.csv",
]

df0 = pd.read_csv(src_paths[0], index_col=0)
df2 = pd.read_csv(src_paths[2], index_col=0)

join_cols = ['admit', 'gre', 'gpa', 'prestige']
df_join = pd.merge(df0, df2, on=join_cols, how='inner', suffixes=('_0', '_2'))

# Load all sources except 2 (already used in join)
dfs = []
for i, path in enumerate(src_paths):
    if i == 2:
        continue
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_union = pd.concat(dfs, ignore_index=True)

df_union.to_csv("autopipeline-benchmarks/github-pipelines/length9_83/target_multisource_mcts.csv", index=False)