import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv", index_col=0)
df_grouped = df0.groupby("V_CALL", as_index=False).size()
df_grouped = df_grouped.rename(columns={"V_CALL": "V_GENE"})
df_grouped = df_grouped[["V_GENE"]]
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_mcts.csv", index=False)