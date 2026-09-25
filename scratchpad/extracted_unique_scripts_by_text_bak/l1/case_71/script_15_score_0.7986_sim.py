import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_71/training_0.csv", index_col=0)
df_grouped = df0.groupby("Region", as_index=False).agg({"Poblacion": "sum", "Superficie": "sum"})
df_grouped["Poblacion"] = df_grouped["Poblacion"].astype(int)
df_grouped["Superficie"] = df_grouped["Superficie"].astype(float)
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_71/target_multisource_mcts.csv", index=False)