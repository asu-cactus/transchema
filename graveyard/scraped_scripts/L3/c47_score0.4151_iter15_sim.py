import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_47/training_1.csv", index_col=0)

agg0 = df0.groupby(['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], as_index=False)[['1970', '2010']].mean()
agg1 = df1.groupby(['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], as_index=False)[['2000', '2015']].mean()

df0_unpivot = agg0.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], value_vars=['1970', '2010'], var_name='Year', value_name='Rural Value')
df1_unpivot = agg1.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], value_vars=['2000', '2015'], var_name='Year', value_name='Electricity Value')

df0_unpivot = df0_unpivot.rename(columns={'Indicator Name': 'Indicator Name 0', 'Indicator Code': 'Indicator Code 0'})
df1_unpivot = df1_unpivot.rename(columns={'Indicator Name': 'Indicator Name 1', 'Indicator Code': 'Indicator Code 1'})

merged = pd.merge(df0_unpivot, df1_unpivot, how='outer', on=['Country Name', 'Country Code', 'Year'])

result = merged[['Country Name', 'Country Code', 'Year', 'Rural Value', 'Electricity Value']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_47/target_multisource_mcts.csv", index=False)