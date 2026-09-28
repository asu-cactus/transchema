import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_34/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_34/training_2.csv", index_col=0)

# Rename J_CALL to V_GENE in each
df0 = df0.rename(columns={"J_CALL": "V_GENE"})
df1 = df1.rename(columns={"J_CALL": "V_GENE"})
df2 = df2.rename(columns={"J_CALL": "V_GENE"})

# Union all source tables by concatenation
df_union = pd.concat([df0, df1, df2], ignore_index=True)

# Write to target file
df_union.to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv", index=False)