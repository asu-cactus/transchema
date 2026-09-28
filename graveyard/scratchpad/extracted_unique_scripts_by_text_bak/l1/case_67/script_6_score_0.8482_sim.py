import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

agg_df = df.groupby("user_id").agg({
    "sad.depressed": "mean",
    "open.stressed": "mean"
}).reset_index()

agg_df = agg_df.rename(columns={
    "sad.depressed": "sad",
    "open.stressed": "stressed"
})

agg_df["user_id"] = agg_df["user_id"].astype(int)
agg_df["sad"] = agg_df["sad"].astype(float)
agg_df["stressed"] = agg_df["stressed"].astype(float)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)