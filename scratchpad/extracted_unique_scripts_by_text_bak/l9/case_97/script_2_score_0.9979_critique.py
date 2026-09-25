import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_97/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_df = pd.concat(dfs, ignore_index=True)

# Ensure correct dtypes matching target schema
union_df['admit'] = union_df['admit'].astype(int)
union_df['gre'] = union_df['gre'].astype(int)
union_df['gpa'] = union_df['gpa'].astype(float)
union_df['prestige'] = union_df['prestige'].astype(int)

union_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_97/target_multisource_mcts.csv", index=False)