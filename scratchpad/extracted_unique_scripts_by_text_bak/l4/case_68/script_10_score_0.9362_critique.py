import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

# Join on school_name
merged = pd.merge(df0, df1, on="school_name", how="inner")

# Group by school_name and type, aggregate as required
agg = merged.groupby(["school_name", "type"]).agg(
    b_size_avg=("size", "mean"),
    c_budget_sum=("budget", "sum"),
    d_reading_avg=("reading_score", "mean"),
    e_math_avg=("math_score", "mean")
).reset_index()

# Rename columns to match target schema
result = agg.rename(columns={
    "school_name": "school_name",
    "type": "a",
    "b_size_avg": "b",
    "c_budget_sum": "c",
    "d_reading_avg": "d",
    "e_math_avg": "e"
})

# Cast types as per target schema
result["school_name"] = result["school_name"].astype(str)
result["a"] = result["a"].astype(str)
result["b"] = result["b"].astype(int)
result["c"] = result["c"].astype(int)
result["d"] = result["d"].astype(float)
result["e"] = result["e"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)