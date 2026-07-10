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

for i, df in enumerate(dfs):
    dfs[i] = df[['revol_util']]

concat_df = pd.concat(dfs, ignore_index=True)

result = concat_df.groupby('revol_util', as_index=False).size()
result.columns = ['revol_util', 'count']

result = result[['revol_util', 'count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_55/target_multisource_mcts.csv", index=False)