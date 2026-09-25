import pandas as pd

# Read the single source table (if more exist, read and union them all)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_20/training_0.csv", index_col=0)

# If multiple source tables existed, we would union them here, e.g.:
# dfs = [df0, df1, df2, ...]
# df = pd.concat(dfs, ignore_index=True)
# But only one source table is given, so just use df0

grouped = df0.groupby("range_of_shot").agg(
    is_goal=("is_goal", "mean"),
    range_sum=("distance_of_shot", "sum"),
    is_goal_count1=("is_goal", lambda x: x.eq(1).sum())
).reset_index()

grouped["range_of_shot"] = grouped["range_of_shot"].astype(str)
grouped["range_sum"] = grouped["range_sum"].astype(int)
grouped["is_goal_count1"] = grouped["is_goal_count1"].astype(int)
grouped["is_goal"] = grouped["is_goal"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_20/target_multisource_mcts.csv", index=False)