import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)
df_union = df_union.rename(columns={"J_CALL": "V_GENE"})

df_union.to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv", index=False)