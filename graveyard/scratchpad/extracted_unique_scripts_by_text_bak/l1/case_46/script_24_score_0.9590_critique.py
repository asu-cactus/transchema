import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)
agg = df0.groupby("Value Date").agg({"Water Use": "sum", "Power Use": "sum"}).reset_index()
agg.rename(columns={"Value Date": "Date"}, inplace=True)
agg["Date"] = agg["Date"].astype(str)
agg["Water Use"] = agg["Water Use"].astype(float)
agg["Power Use"] = agg["Power Use"].astype(int)
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)