import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_46/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)
result = df_all.groupby('purpose', as_index=False).size().rename(columns={'size':'purpose'})
result = result.rename(columns={'purpose': 'purpose'})
result = result[['purpose']]  # keep only the purpose column as integer

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_46/target_multisource_mcts.csv", index=False)