import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv")
result = df0.groupby("condition", as_index=False)["click"].sum()
result.columns = ["condition", "0"]
result["condition"] = result["condition"].astype(int)
result["0"] = result["0"].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)