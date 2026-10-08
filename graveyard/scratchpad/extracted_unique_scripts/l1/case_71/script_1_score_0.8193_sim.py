import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_71/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_71/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)

df_grouped = df_union.groupby("Region", as_index=False).agg({
    "Poblacion": "sum",
    "Superficie": "sum"
})

df_grouped["Region"] = df_grouped["Region"].astype(str)
df_grouped["Poblacion"] = df_grouped["Poblacion"].astype(int)
df_grouped["Superficie"] = df_grouped["Superficie"].astype(float)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_71/target_multisource_mcts.csv", index=False)