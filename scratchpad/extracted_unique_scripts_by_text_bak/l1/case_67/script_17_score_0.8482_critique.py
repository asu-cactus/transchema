import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_1.csv", index_col=0)

df_joined = pd.merge(df0, df1, on=["user_id", "time"], how="inner", suffixes=('_0', '_1'))

df_joined["sad.depressed"] = df_joined[["sad.depressed_0", "sad.depressed_1"]].mean(axis=1)
df_joined["open.stressed"] = df_joined[["open.stressed_0", "open.stressed_1"]].mean(axis=1)

agg = df_joined.groupby("user_id").agg({"sad.depressed": "mean", "open.stressed": "mean"}).reset_index()

agg = agg.rename(columns={"sad.depressed": "sad", "open.stressed": "stressed"})

agg["user_id"] = agg["user_id"].astype(int)
agg["sad"] = agg["sad"].astype(float)
agg["stressed"] = agg["stressed"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)