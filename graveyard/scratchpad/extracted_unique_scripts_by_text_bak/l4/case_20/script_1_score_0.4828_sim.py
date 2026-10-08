import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_20/training_0.csv", index_col=0)

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