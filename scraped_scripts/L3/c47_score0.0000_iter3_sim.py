import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_47/training_1.csv", index_col=0)

join_keys = ['Country Name', 'Country Code', 'Indicator Name']
df_merged = pd.merge(df0, df1, on=join_keys, suffixes=('_rural', '_electricity'))

years = [str(y) for y in range(1960, 2018)]

df_rural = df_merged.melt(id_vars=join_keys, value_vars=[f"{y}_rural" for y in years], var_name='Year', value_name='Rural Value')
df_rural['Year'] = df_rural['Year'].str.replace('_rural', '')

df_elec = df_merged.melt(id_vars=join_keys, value_vars=[f"{y}_electricity" for y in years], var_name='Year', value_name='Electricity Value')
df_elec['Year'] = df_elec['Year'].str.replace('_electricity', '')

df_final = pd.merge(df_rural, df_elec, on=join_keys + ['Year'], how='outer')

df_final = df_final.rename(columns={'Country Name': 'Country Name', 'Country Code': 'Country Code', 'Year': 'Year',
                                    'Rural Value': 'Rural Value', 'Electricity Value': 'Electricity Value'})

df_final = df_final[['Country Name', 'Country Code', 'Year', 'Rural Value', 'Electricity Value']]

df_final['Year'] = df_final['Year'].astype(str)
df_final['Country Name'] = df_final['Country Name'].astype(str)
df_final['Country Code'] = df_final['Country Code'].astype(str)
df_final['Rural Value'] = df_final['Rural Value'].astype(str)
df_final['Electricity Value'] = df_final['Electricity Value'].astype(str)

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_47/target_multisource_mcts.csv", index=False)