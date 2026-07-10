import pandas as pd

src_paths = {
    "Source9_98_0": "autopipeline-benchmarks/github-pipelines/length9_98/training_0.csv",
    "Source9_98_1": "autopipeline-benchmarks/github-pipelines/length9_98/training_1.csv",
    "Source9_98_2": "autopipeline-benchmarks/github-pipelines/length9_98/training_2.csv",
    "Source9_98_3": "autopipeline-benchmarks/github-pipelines/length9_98/training_3.csv",
    "Source9_98_4": "autopipeline-benchmarks/github-pipelines/length9_98/training_4.csv",
    "Source9_98_5": "autopipeline-benchmarks/github-pipelines/length9_98/training_5.csv",
    "Source9_98_6": "autopipeline-benchmarks/github-pipelines/length9_98/training_6.csv",
    "Source9_98_7": "autopipeline-benchmarks/github-pipelines/length9_98/training_7.csv",
    "Source9_98_8": "autopipeline-benchmarks/github-pipelines/length9_98/training_8.csv",
    "Source9_98_9": "autopipeline-benchmarks/github-pipelines/length9_98/training_9.csv",
}

dfs = []
for i in range(10):
    df = pd.read_csv(src_paths[f"Source9_98_{i}"], index_col=0)
    dfs.append(df)

df_union = pd.concat(dfs, ignore_index=True)

df_union = df_union.astype({'admit': 'int64', 'gre': 'int64', 'gpa': 'float64', 'prestige': 'int64'})

df_union.to_csv("autopipeline-benchmarks/github-pipelines/length9_98/target_multisource_mcts.csv", index=False)