import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)

grouped = df_union.groupby("game_season", dropna=False)

season_sum = grouped.size().rename("season_sum")
is_goal_count1 = grouped["is_goal"].count().rename("is_goal_count1")
is_goal_mean = grouped["is_goal"].mean().rename("is_goal")

result = pd.concat([is_goal_mean, season_sum, is_goal_count1], axis=1).reset_index()

result["season_sum"] = result["season_sum"].astype(int)
result["is_goal_count1"] = result["is_goal_count1"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)