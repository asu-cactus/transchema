import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

agg = df.groupby("user_id").agg({
    "sad.depressed": "mean",
    "open.stressed": "mean"
}).reset_index()

agg = agg.rename(columns={"sad.depressed": "sad", "open.stressed": "stressed"})

agg["user_id"] = agg["user_id"].astype(int)
agg["sad"] = agg["sad"].astype(float)
agg["stressed"] = agg["stressed"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)