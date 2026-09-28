import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_9/training_0.csv", index_col=0)

agg_df = df0.groupby("zipcode", as_index=False).agg({
    "zipcode": "sum",
    "AGI_STUB": "sum",
    "N1": "sum",
    "A00100": "sum"
})

agg_df = agg_df[["zipcode", "AGI_STUB", "N1", "A00100"]]

agg_df["zipcode"] = agg_df["zipcode"].astype(int)
agg_df["AGI_STUB"] = agg_df["AGI_STUB"].astype(int)
agg_df["N1"] = agg_df["N1"].astype(int)
agg_df["A00100"] = agg_df["A00100"].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts.csv", index=False)