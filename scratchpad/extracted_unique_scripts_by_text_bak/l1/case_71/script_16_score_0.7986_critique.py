import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_71/training_0.csv", index_col=0)

agg_df = df0.groupby("Region", as_index=False).agg({
    "Poblacion": "sum",
    "Superficie": "sum"
})

agg_df["Poblacion"] = agg_df["Poblacion"].astype(int)
agg_df["Superficie"] = agg_df["Superficie"].astype(float)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_71/target_multisource_mcts.csv", index=False)