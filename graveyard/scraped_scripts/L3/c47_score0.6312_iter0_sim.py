import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_47/training_1.csv", index_col=0)

id_cols = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
value_vars = [col for col in df0.columns if col not in id_cols]

df0_unpivot = df0.melt(id_vars=id_cols, value_vars=value_vars, var_name='Year', value_name='Value')
df1_unpivot = df1.melt(id_vars=id_cols, value_vars=value_vars, var_name='Year', value_name='Value')

df0_pivot = df0_unpivot.pivot_table(index=['Country Name', 'Country Code', 'Year'], 
                                   columns='Indicator Name', values='Value', aggfunc='first').reset_index()
df1_pivot = df1_unpivot.pivot_table(index=['Country Name', 'Country Code', 'Year'], 
                                   columns='Indicator Name', values='Value', aggfunc='first').reset_index()

merged = pd.merge(df0_pivot, df1_pivot, on=['Country Name', 'Country Code', 'Year'], how='outer', suffixes=('_rural', '_electricity'))

merged = merged.rename(columns={
    'Rural population (% of total population)': 'Rural Value',
    'Access to electricity (% of population)': 'Electricity Value'
})

result = merged[['Country Name', 'Country Code', 'Year', 'Rural Value', 'Electricity Value']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_47/target_multisource_mcts.csv", index=False)