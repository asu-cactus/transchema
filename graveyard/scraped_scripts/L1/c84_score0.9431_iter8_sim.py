import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv", index_col=0)
df0 = df0.rename(columns={"V_CALL": "V_GENE"})
df0 = df0[["V_GENE"]]

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_mcts.csv", index=False)