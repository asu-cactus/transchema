import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)

# Group by 'Country / territory of asylum/residence' and sum 'Value'
df_grouped = df0.groupby('Country / territory of asylum/residence', as_index=False)['Value'].sum()

# Rename 'Value' to 'Year' to match target schema
df_grouped = df_grouped.rename(columns={'Value': 'Year'})

# Ensure 'Year' is integer type
df_grouped['Year'] = df_grouped['Year'].astype(int)

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)