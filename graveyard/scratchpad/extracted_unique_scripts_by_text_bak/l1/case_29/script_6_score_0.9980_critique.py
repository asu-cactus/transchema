import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_4.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# GROUP BY Gender and count Purchase ID
result = df_all.groupby('Gender').size().reset_index(name='0')

# Ensure '0' column is integer type
result['0'] = result['0'].astype(int)

# Reorder columns to match target schema
result = result[['Gender', '0']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)