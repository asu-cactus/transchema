import pandas as pd

# Read the single source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv", index_col=0)

# Extract V_GENE from V_CALL
df0['V_GENE'] = df0['V_CALL'].str.split('*').str[0]

# Select only V_GENE column
result = df0[['V_GENE']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_mcts.csv", index=False)