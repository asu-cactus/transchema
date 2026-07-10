import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

# Normalize 'Value Date' format from 'Apr-06' to 'Apr_06' to match target examples
df0["Value Date"] = df0["Value Date"].str.replace("-", "_")

agg = df0.groupby("Value Date", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})

agg = agg.rename(columns={"Value Date": "Date"})

agg = agg[["Date", "Water Use", "Power Use"]]

agg["Date"] = agg["Date"].astype(str)
agg["Water Use"] = agg["Water Use"].astype(float)
agg["Power Use"] = agg["Power Use"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)