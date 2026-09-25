import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_0.csv", index_col=0)  # batsman, batsman_runs
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_3.csv", index_col=0)  # batsman, batsman_runs
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_1.csv", index_col=0)  # batsman, total_runs
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_2.csv", index_col=0)  # batsman, no of balls, batsman_runs, strike
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_4.csv", index_col=0)  # batsman, total_runs

# Rename batsman_runs columns in df0 and df3 to distinguish them before join
df0 = df0.rename(columns={"batsman_runs": "batsman_runs_x"})
df3 = df3.rename(columns={"batsman_runs": "batsman_runs_y"})

# Join df0 and df3 on batsman
join_0_3 = pd.merge(df0, df3, on="batsman", how="inner")

# Join with df1 (total_runs_x)
join_0_3_1 = pd.merge(join_0_3, df1.rename(columns={"total_runs": "total_runs_x"}), on="batsman", how="inner")

# Join with df2 (no of balls, batsman_runs, strike)
join_0_3_1_2 = pd.merge(join_0_3_1, df2, on="batsman", how="inner")

# Join with df4 (total_runs_y)
final_join = pd.merge(join_0_3_1_2, df4.rename(columns={"total_runs": "total_runs_y"}), on="batsman", how="inner")

# Group by batsman and aggregate numeric columns
agg_df = final_join.groupby("batsman", as_index=False).agg({
    "total_runs_x": "sum",
    "batsman_runs_x": "sum",
    "batsman_runs_y": "sum",
    "no of balls": "sum",
    "batsman_runs": "sum",
    "strike": "mean",
    "total_runs_y": "sum"
})

# Reorder columns to match target schema exactly
agg_df = agg_df[[
    "batsman",
    "total_runs_x",
    "batsman_runs_x",
    "batsman_runs_y",
    "no of balls",
    "batsman_runs",
    "strike",
    "total_runs_y"
]]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_34/target_multisource_mcts.csv", index=False)