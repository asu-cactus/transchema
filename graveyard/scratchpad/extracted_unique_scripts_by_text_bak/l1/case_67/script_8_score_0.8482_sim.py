import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="user_id", suffixes=('_left', '_right'))

agg = joined.groupby("user_id").agg({
    "sad.depressed_left": "mean",
    "open.stressed_left": "mean"
}).reset_index()

agg = agg.rename(columns={
    "sad.depressed_left": "sad",
    "open.stressed_left": "stressed"
})

agg["sad"] = agg["sad"].astype(float)
agg["stressed"] = agg["stressed"].astype(float)
agg["user_id"] = agg["user_id"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)