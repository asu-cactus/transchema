import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)

agg_df = df0.groupby("Value Date", as_index=False).agg({"Water Use": "min", "Power Use": "min"})

agg_df = agg_df.rename(columns={"Value Date": "Date", "Water Use": "Water Use", "Power Use": "Power Use"})

agg_df["Date"] = agg_df["Date"].astype(str)
agg_df["Water Use"] = agg_df["Water Use"].astype(float)
agg_df["Power Use"] = agg_df["Power Use"].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)