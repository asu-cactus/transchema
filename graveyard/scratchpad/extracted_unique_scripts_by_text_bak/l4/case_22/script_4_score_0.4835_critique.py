import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_22/training_0.csv", index_col=0)

agg = df0.groupby("type_of_combined_shot").agg(
    shot_sum=pd.NamedAgg(column="shot_id_number", aggfunc="count"),
    is_goal_count1=pd.NamedAgg(column="is_goal", aggfunc="sum"),
    is_goal=pd.NamedAgg(column="is_goal", aggfunc="mean"),
).reset_index()

agg["is_goal"] = agg["is_goal"].astype(float)
agg["shot_sum"] = agg["shot_sum"].astype(int)
agg["is_goal_count1"] = agg["is_goal_count1"].astype(int)
agg["type_of_combined_shot"] = agg["type_of_combined_shot"].astype(str)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_22/target_multisource_mcts.csv", index=False)