import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_71/training_0.csv", index_col=0)

df_agg = df0.groupby("Region", as_index=False).agg({
    "Poblacion": "sum",
    "Superficie": "sum"
})

df_agg["Region"] = df_agg["Region"].astype(str)
df_agg["Poblacion"] = df_agg["Poblacion"].astype(int)
df_agg["Superficie"] = df_agg["Superficie"].astype(float)

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_71/target_multisource_mcts.csv", index=False)