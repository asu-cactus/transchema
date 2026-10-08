import pandas as pd

# Read all three source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_2.csv", index_col=0)

# Union all three sources
df_all = pd.concat([df0, df1, df2], ignore_index=True)

# Group by 'zipcode' and 'AGI_STUB' and sum 'N1' and 'A00100'
result = df_all.groupby(['zipcode', 'AGI_STUB'], as_index=False)[['N1', 'A00100']].sum()

# Ensure correct dtypes as in target schema
result = result.astype({'zipcode': 'int64', 'AGI_STUB': 'int64', 'N1': 'int64', 'A00100': 'int64'})

# Write to output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)