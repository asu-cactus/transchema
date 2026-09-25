import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_3.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_1.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_4.csv", index_col=0)

union_result = pd.concat([df0, df2, df3], ignore_index=True)

join_result_1 = pd.merge(union_result, df1, on="batsman", how="outer")

join_result_2 = pd.merge(join_result_1, df4, on="batsman", how="outer")

result = pd.DataFrame()
result["batsman"] = join_result_2["batsman"]
result["batsman_runs_x"] = join_result_2["batsman_runs_x"] if "batsman_runs_x" in join_result_2 else join_result_2["batsman_runs"]
result["batsman_runs_y"] = join_result_2["batsman_runs_y"] if "batsman_runs_y" in join_result_2 else 0
result["no of balls"] = join_result_2["no of balls"]
result["batsman_runs_x_4"] = join_result_2["batsman_runs_x_4"] if "batsman_runs_x_4" in join_result_2 else 0
result["strike"] = join_result_2["strike"]
result["batsman_runs_y_6"] = join_result_2["batsman_runs_y_6"] if "batsman_runs_y_6" in join_result_2 else 0
result["total_runs"] = join_result_2["total_runs"]

# The unioned tables have only 'batsman' and 'batsman_runs' columns.
# The target schema has batsman_runs_x and batsman_runs_y, which likely come from different source tables.
# We need to separate batsman_runs from different sources into batsman_runs_x and batsman_runs_y.
# Since unioned tables have same schema, we can assign batsman_runs from Source4_35_0 to batsman_runs_x,
# from Source4_35_2 to batsman_runs_y, and from Source4_35_3 to 0 (or vice versa).
# But since union is done, we lost source info. So instead, we do the union with keys to distinguish.

# To fix this, redo union with keys to separate batsman_runs_x and batsman_runs_y:

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_3.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_1.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_4.csv", index_col=0)

df0 = df0.rename(columns={"batsman_runs": "batsman_runs_x"})
df2 = df2.rename(columns={"batsman_runs": "batsman_runs_y"})
df3 = df3.rename(columns={"batsman_runs": "batsman_runs_y"})

union_xy = pd.merge(df0, df2, on="batsman", how="outer")
union_xy = pd.merge(union_xy, df3[["batsman", "batsman_runs_y"]], on="batsman", how="outer", suffixes=("", "_3"))

# Combine batsman_runs_y and batsman_runs_y_3 by filling NaNs with 0 and summing
union_xy["batsman_runs_y_3"] = union_xy["batsman_runs_y_3"].fillna(0)
union_xy["batsman_runs_y"] = union_xy["batsman_runs_y"].fillna(0)
union_xy["batsman_runs_y"] = union_xy["batsman_runs_y"] + union_xy["batsman_runs_y_3"]
union_xy = union_xy.drop(columns=["batsman_runs_y_3"])

join_1 = pd.merge(union_xy, df1, on="batsman", how="outer")

join_2 = pd.merge(join_1, df4, on="batsman", how="outer")

# For batsman_runs_x_4 and batsman_runs_y_6, these columns do not exist in sources.
# Possibly batsman_runs_x_4 and batsman_runs_y_6 are derived from batsman_runs_x and batsman_runs_y respectively.
# Since no source columns named batsman_runs_x_4 or batsman_runs_y_6, we set them to 0.

result = pd.DataFrame()
result["batsman"] = join_2["batsman"]
result["batsman_runs_x"] = join_2["batsman_runs_x"].fillna(0).astype(int)
result["batsman_runs_y"] = join_2["batsman_runs_y"].fillna(0).astype(int)
result["no of balls"] = join_2["no of balls"].fillna(0).astype(int)
result["batsman_runs_x_4"] = 0
result["strike"] = join_2["strike"].astype(float)
result["batsman_runs_y_6"] = 0
result["total_runs"] = join_2["total_runs"].fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_35/target_multisource_mcts.csv", index=False)