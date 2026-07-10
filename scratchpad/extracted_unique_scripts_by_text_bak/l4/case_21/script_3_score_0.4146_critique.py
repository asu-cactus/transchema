import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_21/training_0.csv", index_col=0)

grouped = df.groupby("game_season", dropna=False)

is_goal_mean = grouped["is_goal"].mean().rename("is_goal")
season_sum = grouped["match_event_id"].count().rename("season_sum")
is_goal_count1 = grouped["is_goal"].count().rename("is_goal_count1")

result = pd.concat([grouped.size().rename("dummy"), is_goal_mean, season_sum, is_goal_count1], axis=1)
# The dummy column is not needed, drop it
result = result.drop(columns=["dummy"]).reset_index()

result["season_sum"] = result["season_sum"].astype(int)
result["is_goal_count1"] = result["is_goal_count1"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_21/target_multisource_mcts.csv", index=False)