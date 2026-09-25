import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_71/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_71/training_0.csv", index_col=0)

union_df = pd.concat([df0, df1], ignore_index=True)

agg_df = union_df.groupby("Region", as_index=False).agg({
    "Poblacion": "sum",
    "Superficie": "sum"
})

agg_df["Poblacion"] = agg_df["Poblacion"].astype(int)
agg_df["Superficie"] = agg_df["Superficie"].astype(float)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_71/target_multisource_mcts.csv", index=False)