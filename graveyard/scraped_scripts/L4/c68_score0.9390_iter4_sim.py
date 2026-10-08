import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

agg_source1 = source1.groupby("school_name").agg(
    b=("Student ID", "count"),
    d=("reading_score", "mean"),
    e=("math_score", "mean")
).reset_index()

agg_source0 = source0[["school_name", "type", "size"]]

merged = pd.merge(agg_source1, agg_source0, on="school_name", how="inner")

merged["a"] = merged["type"]
merged["c"] = merged["size"].astype(int)

target = merged[["school_name", "a", "b", "c", "d", "e"]]

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)