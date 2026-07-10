import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_4.csv", index_col=0)

# Rename batsman_runs columns to match target schema columns
df0 = df0.rename(columns={"batsman_runs": "batsman_runs_x"})
df3 = df3.rename(columns={"batsman_runs": "batsman_runs_y"})
df2 = df2.rename(columns={"batsman_runs": "batsman_runs_y_6"})
df4 = df4.rename(columns={"batsman_runs": "batsman_runs_x_4"})

# Join df0 and df3 on batsman
join_0_3 = pd.merge(df0, df3[["batsman", "batsman_runs_y"]], on="batsman", how="outer")

# Join the above with df2 on batsman
join_0_3_2 = pd.merge(join_0_3, df2[["batsman", "batsman_runs_y_6"]], on="batsman", how="outer")

# Join with df1 on batsman (has total_runs)
join_0_3_2_1 = pd.merge(join_0_3_2, df1[["batsman", "total_runs"]], on="batsman", how="outer")

# Join with df4 on batsman (has no of balls, batsman_runs_x_4, strike)
join_all = pd.merge(join_0_3_2_1, df4[["batsman", "no of balls", "batsman_runs_x_4", "strike"]], on="batsman", how="outer")

# Group by batsman and aggregate as per plan
result = join_all.groupby("batsman", as_index=False).agg({
    "batsman_runs_x": "sum",
    "batsman_runs_y": "sum",
    "no of balls": "sum",
    "batsman_runs_x_4": "sum",
    "strike": "mean",
    "batsman_runs_y_6": "sum",
    "total_runs": "sum"
})

# Ensure correct dtypes
result["batsman_runs_x"] = result["batsman_runs_x"].fillna(0).astype(int)
result["batsman_runs_y"] = result["batsman_runs_y"].fillna(0).astype(int)
result["no of balls"] = result["no of balls"].fillna(0).astype(int)
result["batsman_runs_x_4"] = result["batsman_runs_x_4"].fillna(0).astype(int)
result["strike"] = result["strike"].astype(float)
result["batsman_runs_y_6"] = result["batsman_runs_y_6"].fillna(0).astype(int)
result["total_runs"] = result["total_runs"].fillna(0).astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_35/target_multisource_mcts.csv", index=False)