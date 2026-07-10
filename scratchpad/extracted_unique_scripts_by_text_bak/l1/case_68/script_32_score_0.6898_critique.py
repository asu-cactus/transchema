import pandas as pd

# Read all source tables (assuming 3 sources as per instructions, adjust if more)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_2.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2], ignore_index=True)

# Extract V_GENE from V_CALL by splitting on '-' then '*'
df_all['V_GENE'] = df_all['V_CALL'].str.split('-', n=1).str[0].str.split('*', n=1).str[0]

# Select only V_GENE column and drop duplicates to match target
result = df_all[['V_GENE']].drop_duplicates().reset_index(drop=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_68/target_multisource_mcts.csv", index=False)