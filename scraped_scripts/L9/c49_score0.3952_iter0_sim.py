import pandas as pd

files = [
    "autopipeline-benchmarks/github-pipelines/length9_49/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_14.csv"
]

dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby('emp_title', as_index=False).size()
result.rename(columns={'size': 'emp_title'}, inplace=True)
result['emp_title'] = 1

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_49/target_multisource_mcts.csv", index=False)