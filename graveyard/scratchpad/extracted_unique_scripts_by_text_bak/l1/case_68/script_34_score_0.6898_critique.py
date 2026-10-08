import pandas as pd

# Read all three source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_2.csv", index_col=0)

# Extract V_GENE from V_CALL for each dataframe
df0 = df0.assign(V_GENE=df0['V_CALL'].str.split('-').str[0])
df1 = df1.assign(V_GENE=df1['V_CALL'].str.split('-').str[0])
df2 = df2.assign(V_GENE=df2['V_CALL'].str.split('-').str[0])

# Union all dataframes by concatenation
result = pd.concat([df0[['V_GENE']], df1[['V_GENE']], df2[['V_GENE']]], ignore_index=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_68/target_multisource_mcts.csv", index=False)