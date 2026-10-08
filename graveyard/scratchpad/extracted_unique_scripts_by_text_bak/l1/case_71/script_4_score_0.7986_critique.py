import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_71/training_0.csv", index_col=0)

# Normalize Region column by stripping spaces
df0["Region"] = df0["Region"].str.strip()

grouped = df0.groupby("Region", as_index=False).agg({"Poblacion": "sum", "Superficie": "sum"})

grouped["Poblacion"] = grouped["Poblacion"].astype(int)
grouped["Superficie"] = grouped["Superficie"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_71/target_multisource_mcts.csv", index=False)