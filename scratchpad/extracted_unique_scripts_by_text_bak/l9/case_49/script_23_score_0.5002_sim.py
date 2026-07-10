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
    "autopipeline-benchmarks/github-pipelines/length9_49/training_14.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

counts = []
for i, df in enumerate(dfs):
    count_df = df.groupby("emp_title").size().reset_index(name=f"count_{i}")
    counts.append(count_df)

from functools import reduce
merged = reduce(lambda left, right: pd.merge(left, right, on="emp_title", how="outer"), counts)
merged = merged.fillna(0)

merged["emp_title"] = merged["emp_title"].astype(int)
merged["emp_title"] = merged.iloc[:, 1:].sum(axis=1).astype(int)

result = merged[["emp_title"]].copy()
result.columns = ["emp_title"]
result = result.rename(columns={"emp_title": "emp_title"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_49/target_multisource_mcts.csv", index=False)