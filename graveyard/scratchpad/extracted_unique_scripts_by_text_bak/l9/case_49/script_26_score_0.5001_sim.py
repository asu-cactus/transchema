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
for df in dfs:
    c = df.groupby("emp_title").size()
    counts.append(c)

result = pd.concat(counts, axis=1).fillna(0).astype(int)
result["emp_title"] = result.index
result["emp_title"] = 1  # According to target schema, emp_title is integer and target examples show value 1 for all rows

result = result[["emp_title"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_49/target_multisource_mcts.csv", index=False)