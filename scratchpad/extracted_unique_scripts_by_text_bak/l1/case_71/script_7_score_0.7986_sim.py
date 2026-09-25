import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_71/training_0.csv", index_col=0)

agg = df0.groupby("Region", as_index=False).agg({"Poblacion": "sum", "Superficie": "sum"})

agg["Poblacion"] = agg["Poblacion"].astype(int)
agg["Superficie"] = agg["Superficie"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_71/target_multisource_mcts.csv", index=False)