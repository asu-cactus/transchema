import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_24/training_1.csv", index_col=0)

# Join on school_name (inner join to keep only matching schools)
df_joined = pd.merge(df0, df1, on="school_name", how="inner")

# Group by school_name and aggregate:
# - Student ID: take minimum (representative student)
# - budget: sum (budget per school from df1, each school appears once, so sum is safe)
# - math_score: mean
# - reading_score: mean
agg = df_joined.groupby("school_name").agg({
    "Student ID": "min",
    "budget": "sum",
    "math_score": "mean",
    "reading_score": "mean"
}).reset_index()

# Cast columns to match target schema types
agg["Student ID"] = agg["Student ID"].astype(int)
agg["budget"] = agg["budget"].astype(int)
agg["math_score"] = agg["math_score"].astype(float)
agg["reading_score"] = agg["reading_score"].astype(float)

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_24/target_multisource_mcts.csv", index=False)