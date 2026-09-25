import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)

# Convert year to int (if not already)
df = df[df["year"].notna()]  # remove rows with NaN year
df = df[df["year"] != 0]     # remove rows with year=0 if any

df["year"] = df["year"].astype(int)

# Group by year and count movie_id (or any column) occurrences
result = df.groupby("year").size().reset_index(name="0")

result["0"] = result["0"].astype(int)
result["year"] = result["year"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)