import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_47/training_1.csv", index_col=0)

id_cols = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
value_vars = [col for col in df0.columns if col not in id_cols]

df0_unpivot = df0.melt(id_vars=id_cols, value_vars=value_vars, var_name='Year', value_name='Value')
df1_unpivot = df1.melt(id_vars=id_cols, value_vars=value_vars, var_name='Year', value_name='Value')

# Filter to keep only relevant indicators for clarity (optional, but not hardcoded)
# Actually, no filtering needed because we rename after join.

# Rename the 'Value' column to distinguish before join
df0_unpivot = df0_unpivot.rename(columns={'Value': 'Rural Value'})
df1_unpivot = df1_unpivot.rename(columns={'Value': 'Electricity Value'})

# Select only needed columns for join
df0_sel = df0_unpivot[['Country Name', 'Country Code', 'Year', 'Rural Value']]
df1_sel = df1_unpivot[['Country Name', 'Country Code', 'Year', 'Electricity Value']]

# Inner join on keys to avoid extra rows with NaN
merged = pd.merge(df0_sel, df1_sel, on=['Country Name', 'Country Code', 'Year'], how='inner')

# Write output with exact target schema column order
merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_47/target_multisource_mcts.csv", index=False)