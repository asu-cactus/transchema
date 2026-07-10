import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)
agg = df.groupby("Text Date", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})
agg.columns = ["Date", "Water Use", "Power Use"]
agg["Water Use"] = agg["Water Use"].astype(float)
agg["Power Use"] = agg["Power Use"].astype(int)
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)