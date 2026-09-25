import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)
df0_grouped = df0.groupby(['Country / territory of asylum/residence', 'Year'], as_index=False)['Value'].sum()
df0_grouped['Year'] = df0_grouped['Year'].astype(int)
df0_grouped.rename(columns={'Value': 'Year'}, inplace=False)  # No rename needed, target schema is ['Country / territory of asylum/residence', 'Year']

df0_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)