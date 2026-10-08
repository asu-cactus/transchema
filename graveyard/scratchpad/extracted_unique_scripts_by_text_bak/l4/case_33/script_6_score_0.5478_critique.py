import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_0.csv", index_col=0)  # batsman, batsman_runs (float/int)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_3.csv", index_col=0)  # batsman, batsman_runs (int)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_4.csv", index_col=0)  # batsman, batsman_runs (float)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_1.csv", index_col=0)  # batsman, total_runs (int)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_2.csv", index_col=0)  # batsman, total_runs (int)

# Join s0 and s3 on batsman to get batsman_runs_x and batsman_runs_y
batsman_runs_join = pd.merge(s0, s3, on="batsman", how="inner", suffixes=('_x', '_y'))

# Join the above with s4 to get batsman_runs (the last batsman_runs column)
batsman_runs_join = pd.merge(batsman_runs_join, s4, on="batsman", how="inner", suffixes=('', '_z'))

# Rename s4 batsman_runs to 'batsman_runs' (no suffix)
batsman_runs_join = batsman_runs_join.rename(columns={"batsman_runs": "batsman_runs"})

# Join s1 and s2 on batsman to get total_runs_x and total_runs_y
total_runs_join = pd.merge(s1, s2, on="batsman", how="inner", suffixes=('_x', '_y'))

# Join batsman_runs_join and total_runs_join on batsman
df = pd.merge(batsman_runs_join, total_runs_join, on="batsman", how="inner")

# Select and reorder columns to match target schema:
# ['batsman': string, 'batsman_runs_x': float, 'total_runs_x': integer, 'total_runs_y': integer, 'batsman_runs_y': integer, 'batsman_runs': integer]

# Convert types accordingly:
df["batsman_runs_x"] = df["batsman_runs_x"].astype(float)
df["total_runs_x"] = df["total_runs_x"].astype("Int64")
df["total_runs_y"] = df["total_runs_y"].astype("Int64")
df["batsman_runs_y"] = df["batsman_runs_y"].astype("Int64")
# The last batsman_runs column (from s4) is float, but target shows integer, so convert to Int64
df["batsman_runs"] = df["batsman_runs"].astype("Int64")

df = df[["batsman", "batsman_runs_x", "total_runs_x", "total_runs_y", "batsman_runs_y", "batsman_runs"]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_33/target_multisource_mcts.csv", index=False)