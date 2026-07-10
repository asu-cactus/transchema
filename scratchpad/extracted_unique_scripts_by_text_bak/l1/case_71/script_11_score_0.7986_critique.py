import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_71/training_0.csv", index_col=0)

df0["Region"] = df0["Region"].str.strip()

result = df0.groupby("Region", as_index=False).agg({
    "Poblacion": "sum",
    "Superficie": "sum"
})

result["Poblacion"] = result["Poblacion"].astype(int)
result["Superficie"] = result["Superficie"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_71/target_multisource_mcts.csv", index=False)