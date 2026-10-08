import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)

agg_df = df.groupby("Text Date", as_index=False).agg({
    "Water Use": "mean",
    "Power Use": "mean"
})

agg_df["Date"] = agg_df["Text Date"]
agg_df = agg_df.drop(columns=["Text Date"])

agg_df["Water Use"] = agg_df["Water Use"].astype(float)
agg_df["Power Use"] = agg_df["Power Use"].round().astype(int)
agg_df["Date"] = agg_df["Date"].astype(str)

agg_df = agg_df[["Date", "Water Use", "Power Use"]]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)