import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_47/training_1.csv", index_col=0)

id_cols = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
year_cols = [col for col in df0.columns if col not in id_cols]

# Melt both source tables to long format
df0_melt = df0.melt(id_vars=id_cols, value_vars=year_cols, var_name='Year', value_name='Value')
df1_melt = df1.melt(id_vars=id_cols, value_vars=year_cols, var_name='Year', value_name='Value')

# UNION the two melted dataframes
df_union = pd.concat([df0_melt, df1_melt], ignore_index=True)

# Pivot the unioned dataframe to get indicators as columns
df_pivot = df_union.pivot_table(index=['Country Name', 'Country Code', 'Year'],
                               columns='Indicator Name', values='Value', aggfunc='first').reset_index()

# Rename columns to match target schema
df_pivot = df_pivot.rename(columns={
    'Rural population (% of total population)': 'Rural Value',
    'Access to electricity (% of population)': 'Electricity Value'
})

# Select and order columns as per target schema
df_final = df_pivot[['Country Name', 'Country Code', 'Year', 'Rural Value', 'Electricity Value']]

# Convert all columns to string type as in target schema
df_final['Country Name'] = df_final['Country Name'].astype(str)
df_final['Country Code'] = df_final['Country Code'].astype(str)
df_final['Year'] = df_final['Year'].astype(str)
df_final['Rural Value'] = df_final['Rural Value'].astype(str)
df_final['Electricity Value'] = df_final['Electricity Value'].astype(str)

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_47/target_multisource_mcts.csv", index=False)