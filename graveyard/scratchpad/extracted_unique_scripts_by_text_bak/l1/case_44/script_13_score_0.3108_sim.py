import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)

# The partial plan suggests a self-join on 'Country / territory of asylum/residence' and 'Year', which is redundant here.
# Instead, we interpret this as grouping by these columns and aggregating 'Value' (sum) to get the target schema.

df0['Value'] = pd.to_numeric(df0['Value'], errors='coerce')
grouped = df0.groupby(['Country / territory of asylum/residence', 'Year'], as_index=False)['Value'].sum()

# Rename columns to match target schema exactly
result = grouped.rename(columns={'Value': 'Year'})  # But target schema Year is integer, so this is wrong.

# The target schema is ['Country / territory of asylum/residence': string, 'Year': integer]
# The target examples show 'Year' column with large numbers like 9195455, 4694665, 211552 which look like aggregated values, not years.
# So the target 'Year' column is actually the aggregated 'Value' column from source, but named 'Year' in target.
# The source 'Year' column is the actual year (e.g., 2012), but target 'Year' column is the aggregated value.

# So we must rename 'Value' sum to 'Year' and keep 'Country / territory of asylum/residence' as is.

result = grouped.rename(columns={'Value': 'Year'})

# Ensure 'Year' column is integer type
result['Year'] = result['Year'].fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)