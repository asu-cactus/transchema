import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

df = df.rename(columns={"Text Date": "Date"})

df = df.groupby("Date", as_index=False).agg({
    "Water Use": "sum",
    "Power Use": "sum"
})

df["Water Use"] = df["Water Use"].astype(float)
df["Power Use"] = df["Power Use"].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)