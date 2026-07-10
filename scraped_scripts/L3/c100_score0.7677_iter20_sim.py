import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_2.csv", index_col=0)

# The partial plan suggests UNION of Source3_100_1 and Source3_100_2, but their schemas differ:
# Source1 columns: ['Country', 'Energy Supply', 'Energy Supply per Capita', '% Renewable']
# Source2 columns: ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code', '1960', ..., '2015']
# They cannot be unioned directly. Instead, we must join all sources on country-related keys.

# Step 1: Normalize country column names for joining
df1_renamed = df1.rename(columns={'Country': 'Country'})
df2_renamed = df2.rename(columns={'Country Name': 'Country'})

# Step 2: Join df0 with df1 on 'Country' (df0 has 'Country', df1 has 'Country')
df0_1 = pd.merge(df0, df1_renamed, on='Country', how='inner')

# Step 3: Pivot df2 to long format to get indicator values by year, then filter or aggregate as needed
# But target schema only has 'Rank' and '0' columns, so we need to find what '0' means.

# The target schema is ['Rank': int, '0': int]
# From the example, '0' column is always 1 in the sample, so likely a count or indicator presence.

# Since the partial plan says UNION of Source3_100_1 and Source3_100_2, then PIVOT, then GROUP_BY Rank,
# but these two sources have different schemas, so UNION is not possible.

# Instead, we can interpret the plan as:
# - UNION the two source tables that have similar schema (Source3_100_1 and Source3_100_2) after some transformation
# - PIVOT the unioned data to get a table with 'Rank' and '0' columns
# - GROUP_BY Rank to aggregate

# But Source3_100_1 and Source3_100_2 do not have Rank column.
# Only Source3_100_0 has Rank.

# So likely the plan is:
# - Join Source3_100_0 with Source3_100_1 and Source3_100_2 on country columns
# - Then transform to get the target schema

# Let's join df0 with df1 on 'Country'
df0_1 = pd.merge(df0, df1, on='Country', how='inner')

# For df2, we need to reshape it to long format to get indicator values per country
df2_long = df2.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], 
                    var_name='Year', value_name='Value')
df2_long = df2_long.rename(columns={'Country Name': 'Country'})

# We can filter df2_long to keep only rows where Indicator Name or Code matches something relevant,
# but since target schema is only Rank and 0, and 0 is integer 1 in examples,
# it suggests the target is a count or flag per Rank.

# So let's join df0_1 with df2_long on 'Country'
df_merged = pd.merge(df0_1, df2_long, on='Country', how='inner')

# Now, create a column '0' with value 1 as in target examples
df_merged['0'] = 1

# Select only 'Rank' and '0' columns
df_result = df_merged[['Rank', '0']]

# Group by Rank and sum '0' to aggregate counts if duplicates exist
df_final = df_result.groupby('Rank', as_index=False).sum()

# Ensure 'Rank' and '0' are integers
df_final['Rank'] = df_final['Rank'].astype(int)
df_final['0'] = df_final['0'].astype(int)

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_100/target_multisource_mcts.csv", index=False)