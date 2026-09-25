import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_47/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_47/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length3_47/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

id_cols = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
year_cols = [col for col in df0.columns if col not in id_cols]

# Melt both dataframes to long format with a common value column name and indicator column
df0_melted = df0.melt(id_vars=id_cols, value_vars=year_cols, var_name='Year', value_name='Value')
df1_melted = df1.melt(id_vars=id_cols, value_vars=year_cols, var_name='Year', value_name='Value')

# Concatenate the two melted dataframes (UNION)
union_df = pd.concat([df0_melted, df1_melted], ignore_index=True)

# Pivot so that Indicator Name becomes columns, values are from 'Value'
pivot_df = union_df.pivot_table(
    index=['Country Name', 'Country Code', 'Year'],
    columns='Indicator Name',
    values='Value',
    aggfunc='first'  # There should be only one value per group
).reset_index()

# Rename columns to match target schema
pivot_df = pivot_df.rename(columns={
    'Rural population (% of total population)': 'Rural Value',
    'Access to electricity (% of population)': 'Electricity Value'
})

# Keep only rows where both Rural Value and Electricity Value are present (non-NaN)
result = pivot_df.dropna(subset=['Rural Value', 'Electricity Value'])

# Reorder columns to match target schema
result = result[['Country Name', 'Country Code', 'Year', 'Rural Value', 'Electricity Value']]

result.to_csv(target_path, index=False)