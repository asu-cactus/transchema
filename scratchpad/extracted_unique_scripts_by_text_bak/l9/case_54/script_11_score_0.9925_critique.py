import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_54/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_result = pd.concat(dfs, ignore_index=True)

# The target schema is ['earliest_cr_line'], so just output the unioned dataframe as is
union_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_54/target_multisource_mcts.csv", index=False)