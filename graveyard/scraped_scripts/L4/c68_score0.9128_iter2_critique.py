import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="school_name")

agg = merged.groupby(["school_name", "type"]).agg({
    "size": "sum",
    "budget": "sum",
    "reading_score": "mean",
    "math_score": "mean"
}).reset_index()

agg = agg.rename(columns={
    "type": "a",
    "size": "b",
    "budget": "c",
    "reading_score": "d",
    "math_score": "e"
})

result = agg[["school_name", "a", "b", "c", "d", "e"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)