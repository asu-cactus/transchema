import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_71/training_0.csv", index_col=0)

# Strip whitespace from Region to ensure matching keys
df0["Region"] = df0["Region"].str.strip()

agg = df0.groupby("Region").agg({"Poblacion": "sum", "Superficie": "sum"}).reset_index()

agg["Poblacion"] = agg["Poblacion"].astype(int)
agg["Superficie"] = agg["Superficie"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_71/target_multisource_mcts.csv", index=False)