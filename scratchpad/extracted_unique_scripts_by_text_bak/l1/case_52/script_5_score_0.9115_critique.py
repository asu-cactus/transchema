import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)

result = df.groupby("condition", as_index=False).agg({"click": "count"}).rename(columns={"click": "0"})

result["condition"] = result["condition"].astype(int)
result["0"] = result["0"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)