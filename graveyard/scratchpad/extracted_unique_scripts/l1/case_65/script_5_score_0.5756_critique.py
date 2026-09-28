import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)

# Convert 'year' to numeric, coercing errors to NaN, then drop NaN years
df["year"] = pd.to_numeric(df["year"], errors='coerce')
df = df.dropna(subset=["year"])

# Convert year to int (safe after dropping NaN)
df["year"] = df["year"].astype(int)

# Group by 'year' and count the number of rows per year
result = df.groupby("year", as_index=False).agg({"year": "count"})

# Rename the count column to '0' as per target schema
result = result.rename(columns={"year": "0"})

# Ensure '0' is integer type
result["0"] = result["0"].astype(int)

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)