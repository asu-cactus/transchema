import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

grouped = df0.groupby("game_season", dropna=False).agg(
    is_goal=("is_goal", "mean"),
    season_sum=("is_goal", "sum"),
    is_goal_count1=("is_goal", "count")
).reset_index()

grouped["season_sum"] = grouped["season_sum"].astype("Int64")
grouped["is_goal_count1"] = grouped["is_goal_count1"].astype("Int64")
grouped["game_season"] = grouped["game_season"].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)