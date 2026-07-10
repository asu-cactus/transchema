import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

agg_scores = df1.groupby("school_name").agg(reading_score_avg=("reading_score", "mean"), math_score_avg=("math_score", "mean")).reset_index()

agg0 = df0.groupby(["school_name", "type"]).agg(
    a_size_avg=("size", "mean"),
    b_budget_sum=("budget", "sum")
).reset_index()

merged = pd.merge(agg0, agg_scores, on="school_name", how="inner")

result = merged.rename(columns={
    "school_name": "school_name",
    "type": "a",
    "a_size_avg": "b",
    "b_budget_sum": "c",
    "reading_score_avg": "d",
    "math_score_avg": "e"
})

result["b"] = result["b"].astype(int)
result["c"] = result["c"].astype(int)
result["a"] = result["a"].astype(str)
result["school_name"] = result["school_name"].astype(str)
result["d"] = result["d"].astype(float)
result["e"] = result["e"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)