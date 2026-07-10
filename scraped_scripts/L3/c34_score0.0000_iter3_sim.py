import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_1.csv", index_col=0)

join_cols = ['Country Name', 'Country Code']
df = pd.merge(df0, df1, on=join_cols, suffixes=('_rural', '_electricity'))

years = [str(y) for y in range(1960, 2018)]

df_rural = df.melt(id_vars=join_cols + ['Indicator Name_rural'], value_vars=years,
                   var_name='Year', value_name='Rural Value')
df_elec = df.melt(id_vars=join_cols + ['Indicator Name_electricity'], value_vars=years,
                  var_name='Year', value_name='Electricity Value')

df_rural = df_rural.rename(columns={'Indicator Name_rural': 'Indicator Name'})
df_elec = df_elec.rename(columns={'Indicator Name_electricity': 'Indicator Name'})

df_merged = pd.merge(df_rural, df_elec, on=join_cols + ['Year'], how='outer')

df_merged = df_merged[['Country Name', 'Country Code', 'Year', 'Rural Value', 'Electricity Value']]

df_merged['Year'] = df_merged['Year'].astype(str)
df_merged['Country Name'] = df_merged['Country Name'].astype(str)
df_merged['Country Code'] = df_merged['Country Code'].astype(str)
df_merged['Rural Value'] = df_merged['Rural Value'].astype(str)
df_merged['Electricity Value'] = df_merged['Electricity Value'].astype(str)

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_34/target_multisource_mcts.csv", index=False)