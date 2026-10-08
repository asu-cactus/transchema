import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

agg_df = df0.groupby("Text Date", as_index=False).agg({
    "Water Use": "mean",
    "Power Use": "mean"
})

agg_df["Water Use"] = agg_df["Water Use"].astype(float)
agg_df["Power Use"] = agg_df["Power Use"].round().astype(int)
agg_df = agg_df.rename(columns={"Text Date": "Date"})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)