import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)
df0['Value'] = pd.to_numeric(df0['Value'], errors='coerce')
grouped = df0.groupby(['Country / territory of asylum/residence', 'Year'], dropna=False, as_index=False)['Value'].sum()
grouped.rename(columns={'Value': 'Year'}, inplace=False)  # no rename needed, target schema is ['Country / territory of asylum/residence', 'Year'] with Year as int

grouped['Year'] = pd.to_numeric(grouped['Year'], errors='coerce')
grouped['Year'] = grouped['Year'].fillna(0).astype(int)

grouped.rename(columns={'Value': 'Year'}, inplace=True)
# Actually, the target schema is ['Country / territory of asylum/residence': string, 'Year': integer]
# But from the example, the 'Year' column in target examples contains large numbers like 10937520, 5663087, 495061
# This suggests the target 'Year' column is actually the aggregated sum of 'Value' (not the year number)
# So the target schema's 'Year' column is actually the sum of 'Value' per country (year is aggregated out)
# So the group_by should be only on 'Country / territory of asylum/residence' and sum of 'Value' renamed as 'Year'

# Reconsidering the plan:
# The partial plan groups by Country, Origin, Month, Value and sums Value, but target schema only has Country and Year (integer)
# The target examples show 'Year' column with large numbers, which are sums of Value, not the year number
# So we should group by 'Country / territory of asylum/residence' only, sum 'Value' and rename sum as 'Year'

df0['Value'] = pd.to_numeric(df0['Value'], errors='coerce')
agg = df0.groupby('Country / territory of asylum/residence', dropna=False)['Value'].sum().reset_index()
agg.rename(columns={'Value': 'Year'}, inplace=True)
agg['Year'] = agg['Year'].fillna(0).astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)