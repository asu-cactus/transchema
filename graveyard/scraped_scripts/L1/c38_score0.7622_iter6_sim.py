import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)
agg = df0.groupby("user_id").agg({
    "sad.depressed": "sum",
    "open.stressed": "sum"
}).reset_index()
agg.columns = ["user_id", "sad", "stressed"]
agg["user_id"] = agg["user_id"].astype(int)
agg["sad"] = agg["sad"].astype(float)
agg["stressed"] = agg["stressed"].astype(float)
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)