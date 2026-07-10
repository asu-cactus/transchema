import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_0.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_4.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_2.csv", index_col=0)

union_result = pd.concat([s0, s3, s4], ignore_index=True)

join_result_1 = pd.merge(union_result, s1, on="batsman", how="outer", suffixes=('_x', '_y'))
join_result_2 = pd.merge(join_result_1, s2, on="batsman", how="outer", suffixes=('_x', '_y'))

# Rename columns to match target schema
# Target schema: ['batsman': string, 'batsman_runs_x': float, 'total_runs_x': integer, 'total_runs_y': integer, 'batsman_runs_y': integer, 'batsman_runs': integer]

# After merges, columns are:
# batsman
# batsman_runs_x (from union_result)
# batsman_runs_y (from s1 merge suffix, but s1 has no batsman_runs, so no)
# total_runs (from s1)
# total_runs_y (from s2)
# batsman_runs_y (from s2 merge suffix? s2 has no batsman_runs)
# Actually, s1 and s2 have 'total_runs' only, so suffixes apply to total_runs columns.

# So after first merge:
# columns: batsman, batsman_runs (from union_result), total_runs (from s1)
# after second merge:
# columns: batsman, batsman_runs, total_runs_x (from s1), total_runs_y (from s2)

# But suffixes in second merge are ('_x', '_y'), so total_runs from s1 becomes total_runs_x, from s2 total_runs_y

# The union_result has batsman_runs only, no total_runs, so no suffix for batsman_runs.

# The target also has batsman_runs_y and batsman_runs (integer). The source tables do not have batsman_runs_y except suffixes from merges.

# We have batsman_runs from union_result (float and int mixed), total_runs_x (int), total_runs_y (int).

# The target has batsman_runs_x (float), total_runs_x (int), total_runs_y (int), batsman_runs_y (int), batsman_runs (int).

# We have only one batsman_runs column from union_result, which we can rename to batsman_runs_x (float).

# The batsman_runs_y and batsman_runs (int) columns do not exist in sources, so we create them as 0 (integer) as in target examples.

# Convert types accordingly.

df = join_result_2.rename(columns={"batsman_runs": "batsman_runs_x"})

df["batsman_runs_x"] = df["batsman_runs_x"].astype(float)
df["total_runs_x"] = df["total_runs_x"].astype("Int64")
df["total_runs_y"] = df["total_runs_y"].astype("Int64")

df["batsman_runs_y"] = 0
df["batsman_runs"] = 0

df = df[["batsman", "batsman_runs_x", "total_runs_x", "total_runs_y", "batsman_runs_y", "batsman_runs"]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_33/target_multisource_mcts.csv", index=False)