import pandas as pd

paths = [
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

dfs = [pd.read_csv(p, index_col=0) for p in paths]

for i, df in enumerate(dfs):
    dfs[i] = df.groupby('emp_title', as_index=False).size().rename(columns={'size': f'emp_title_{i}'})

merged = dfs[0]
for i in range(1, len(dfs)):
    merged = pd.merge(merged, dfs[i], on='emp_title', how='outer')

merged.fillna(0, inplace=True)

merged['emp_title'] = merged[[f'emp_title_{i}' for i in range(len(dfs))]].sum(axis=1).astype(int)

result = merged[['emp_title']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_49/target_multisource_mcts.csv", index=False)