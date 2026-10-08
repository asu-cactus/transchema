import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)
agg = df0.groupby("Value Date", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})
agg = agg.rename(columns={"Value Date": "Date", "Water Use": "Water Use", "Power Use": "Power Use"})
agg["Date"] = agg["Date"].astype(str)
agg["Water Use"] = agg["Water Use"].astype(float)
agg["Power Use"] = agg["Power Use"].astype(int)
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)