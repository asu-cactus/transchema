import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_0.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_3.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_2.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_4.csv", index_col=0)

union_df = pd.concat([df0, df3], ignore_index=True)

join_1 = pd.merge(union_df, df1, on="batsman", how="inner")
join_2 = pd.merge(join_1, df2, on="batsman", how="inner")
final_df = pd.merge(join_2, df4, on="batsman", how="inner")

final_df = final_df.rename(columns={
    "total_runs_x": "total_runs_x",
    "batsman_runs_x": "batsman_runs_x",
    "batsman_runs_y": "batsman_runs_y",
    "no of balls": "no of balls",
    "batsman_runs": "batsman_runs",
    "strike": "strike",
    "total_runs_y": "total_runs_y"
})

# The union of df0 and df3 both have 'batsman' and 'batsman_runs'.
# After union, the 'batsman_runs' column corresponds to batsman_runs_x and batsman_runs_y in target.
# We need to separate these two columns from unioned data:
# But since union concatenates rows, we have to distinguish batsman_runs_x and batsman_runs_y by source.
# The partial plan suggests union of Source4_34_0 and Source4_34_3, then join with others.
# So we assign batsman_runs_x from Source4_34_0 rows, batsman_runs_y from Source4_34_3 rows.

# To do this, we add a source indicator before union:
df0["source"] = "x"
df3["source"] = "y"
union_df = pd.concat([df0, df3], ignore_index=True)

# Pivot the unioned data to get batsman_runs_x and batsman_runs_y as separate columns
pivot_df = union_df.pivot_table(index="batsman", columns="source", values="batsman_runs", aggfunc='sum').reset_index()
pivot_df = pivot_df.rename(columns={"x": "batsman_runs_x", "y": "batsman_runs_y"})

# Now join pivot_df with df1 (total_runs), df2 (no of balls, batsman_runs, strike), df4 (total_runs)
join_1 = pd.merge(pivot_df, df1, on="batsman", how="inner")
join_2 = pd.merge(join_1, df2, on="batsman", how="inner")
final_df = pd.merge(join_2, df4, on="batsman", how="inner")

# Rename columns to match target schema
final_df = final_df.rename(columns={
    "total_runs_x": "total_runs_x",
    "batsman_runs_x": "batsman_runs_x",
    "batsman_runs_y": "batsman_runs_y",
    "no of balls": "no of balls",
    "batsman_runs": "batsman_runs",
    "strike": "strike",
    "total_runs_y": "total_runs_y"
})

# Ensure correct column order
final_df = final_df[[
    "batsman",
    "total_runs_x",
    "batsman_runs_x",
    "batsman_runs_y",
    "no of balls",
    "batsman_runs",
    "strike",
    "total_runs_y"
]]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_34/target_multisource_mcts.csv", index=False)