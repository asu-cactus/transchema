import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv", index_col=0)

agg = df0.groupby("Source Zipcode")["Counts"].agg(["min", "max"]).reset_index()
agg["Counts"] = agg["min"] + agg["max"]
result = agg[["Source Zipcode", "Counts"]].astype({"Source Zipcode": int, "Counts": int})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)