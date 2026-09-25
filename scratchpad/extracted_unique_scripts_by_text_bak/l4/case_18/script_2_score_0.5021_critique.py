import pandas as pd

# Read the single source table (if multiple, read all and union)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_18/training_0.csv", index_col=0)

# If there were multiple source tables, union them here:
# For example:
# df1 = pd.read_csv("path_to_other_source.csv", index_col=0)
# df = pd.concat([df0, df1], ignore_index=True)
# But since only one source is given, just use df0 as df

df = df0

grouped = df.groupby("area_of_shot").agg(
    is_goal=("is_goal", "mean"),
    area_shot_sum=("area_of_shot", "size"),
    is_goal_count=("is_goal", "count")
).reset_index()

grouped["area_shot_sum"] = grouped["area_shot_sum"].astype(int)
grouped["is_goal_count"] = grouped["is_goal_count"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_18/target_multisource_mcts.csv", index=False)