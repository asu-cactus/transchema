import pandas as pd

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_1.csv", index_col=0)

# Melt both sources to long format
df0_melted = df0.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name'], var_name='Year', value_name='Value')
df1_melted = df1.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name'], var_name='Year', value_name='Value')

# Filter relevant indicators
df0_filtered = df0_melted[df0_melted['Indicator Name'] == 'Rural population (% of total population)']
df1_filtered = df1_melted[df1_melted['Indicator Name'] == 'Access to electricity (% of population)']

# Add a column to identify the indicator type for pivoting
df0_filtered = df0_filtered.assign(IndicatorType='Rural Value')
df1_filtered = df1_filtered.assign(IndicatorType='Electricity Value')

# Select relevant columns
df0_filtered = df0_filtered[['Country Name', 'Country Code', 'Year', 'IndicatorType', 'Value']]
df1_filtered = df1_filtered[['Country Name', 'Country Code', 'Year', 'IndicatorType', 'Value']]

# UNION the two filtered datasets
df_union = pd.concat([df0_filtered, df1_filtered], ignore_index=True)

# Pivot to get Rural Value and Electricity Value columns
df_pivot = df_union.pivot_table(index=['Country Name', 'Country Code', 'Year'],
                                columns='IndicatorType',
                                values='Value',
                                aggfunc='first').reset_index()

# Ensure columns are in target schema order and names
df_pivot.columns.name = None  # remove pivot table column grouping name
df_pivot = df_pivot[['Country Name', 'Country Code', 'Year', 'Rural Value', 'Electricity Value']]

# Convert all columns to string as in target schema
df_pivot = df_pivot.astype(str)

# Write output
df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_34/target_multisource_mcts.csv", index=False)