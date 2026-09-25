import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)

df = df.rename(columns={"Text Date": "Date"})

df_grouped = df.groupby("Date", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})

df_grouped["Water Use"] = df_grouped["Water Use"].astype(float)
df_grouped["Power Use"] = df_grouped["Power Use"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)