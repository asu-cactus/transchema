import pandas as pd

paths_group1 = [
    "autopipeline-benchmarks/github-pipelines/length9_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_16.csv"
]

paths_group2 = [
    "autopipeline-benchmarks/github-pipelines/length9_59/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_14.csv"
]

def load_and_concat(paths):
    dfs = [pd.read_csv(p, index_col=0) for p in paths]
    return pd.concat(dfs, ignore_index=True)

union_1 = load_and_concat(paths_group1)
union_2 = load_and_concat(paths_group2)

final_df = pd.concat([union_1, union_2], ignore_index=True)

final_df['country'] = final_df['country'].astype(str)
final_df['cpi'] = final_df['cpi'].astype(float)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_59/target_multisource_mcts.csv", index=False)