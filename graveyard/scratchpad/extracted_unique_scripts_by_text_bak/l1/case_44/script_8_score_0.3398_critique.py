import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)

# Group by 'Country / territory of asylum/residence' and sum 'Value'
df_agg = df0.groupby('Country / territory of asylum/residence', as_index=False)['Value'].sum()

# Rename 'Value' to 'Year' to match target schema
df_agg.rename(columns={'Value': 'Year'}, inplace=True)

# Ensure 'Year' is integer type
df_agg['Year'] = df_agg['Year'].astype(int)

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)