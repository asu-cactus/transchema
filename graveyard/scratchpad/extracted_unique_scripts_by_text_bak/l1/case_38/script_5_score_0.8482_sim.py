import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="user_id")

agg_df = df_joined.groupby("user_id").agg({
    "sad.depressed_x": "mean",
    "open.stressed_x": "mean"
}).reset_index()

agg_df.rename(columns={
    "sad.depressed_x": "sad",
    "open.stressed_x": "stressed"
}, inplace=True)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)