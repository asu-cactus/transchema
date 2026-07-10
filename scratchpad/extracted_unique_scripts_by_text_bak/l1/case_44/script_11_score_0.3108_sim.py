import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)
df0_grouped = df0.groupby(['Country / territory of asylum/residence', 'Year'], as_index=False)['Value'].sum()
df0_grouped['Year'] = df0_grouped['Year'].astype(int)
df0_grouped.rename(columns={'Value': 'Year'}, inplace=True)
df0_grouped = df0_grouped.rename(columns={'Value': 'Year'})  # This line is redundant, remove it
# Actually, we need to rename the aggregated sum column to 'Year' per target schema? No, target schema is:
# ['Country / territory of asylum/residence': string, 'Year': integer]
# But the example shows 'Year' column contains large numbers like 951946, 15292622, 10323019 which are sums of Value.
# So the sum of Value is stored in 'Year' column in target.
# So we must rename the sum of Value column to 'Year' and keep 'Country / territory of asylum/residence' as is.

df0_grouped = df0_grouped.rename(columns={'Value': 'Year'})

df0_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)