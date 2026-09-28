import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_60/training_0.csv", index_col=0)

filtered = df0[df0["type"] == "Urban"]

result = pd.DataFrame({
    "type": ["Urban"],
    "driver_count": [filtered["driver_count"].sum().astype(int)]
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)