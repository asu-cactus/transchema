import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="school_name")

agg = merged.groupby("school_name").agg({
    "type": "first",
    "size": "sum",
    "reading_score": "sum",
    "math_score": "mean"
}).reset_index()

agg["a"] = agg["type"].astype(str)
agg["b"] = agg["size"].astype(int)
agg["c"] = agg["reading_score"].astype(int)
agg["d"] = agg["math_score"].astype(float)
agg["e"] = agg["math_score"].astype(float)

result = agg[["school_name", "a", "b", "c", "d", "e"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)