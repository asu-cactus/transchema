import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_49/training_0.csv", index_col=0)

agg_df = df0.groupby("title").agg(min_rank=("rank_on_list", "min"), max_weeks_on_list=("weeks_on_list", "max")).reset_index()

agg_df["min_rank"] = agg_df["min_rank"].astype(int)
agg_df["max_weeks_on_list"] = agg_df["max_weeks_on_list"].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_49/target_multisource_mcts.csv", index=False)