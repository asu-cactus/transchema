import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

df = df0.rename(columns={"Text Date": "Date"})

# Group by Date and sum Water Use and Power Use
df_agg = df.groupby("Date", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})

# Ensure correct types
df_agg["Water Use"] = df_agg["Water Use"].astype(float)
df_agg["Power Use"] = df_agg["Power Use"].astype(int)
df_agg["Date"] = df_agg["Date"].astype(str)

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)