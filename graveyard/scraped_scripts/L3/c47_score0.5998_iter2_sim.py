import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_47/training_1.csv", index_col=0)

years = [str(y) for y in range(1960, 2018)]

df0_filtered = df0[df0['Indicator Name'] == 'Rural population (% of total population)']
df0_unpivot = df0_filtered.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], 
                               value_vars=years, var_name='Year', value_name='Rural Value')

df1_filtered = df1[df1['Indicator Name'] == 'Access to electricity (% of population)']
df1_unpivot = df1_filtered.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], 
                               value_vars=years, var_name='Year', value_name='Electricity Value')

merged = pd.merge(df0_unpivot[['Country Name', 'Country Code', 'Year', 'Rural Value']],
                  df1_unpivot[['Country Name', 'Country Code', 'Year', 'Electricity Value']],
                  on=['Country Name', 'Country Code', 'Year'], how='outer')

merged['Year'] = merged['Year'].astype(str)
merged['Country Name'] = merged['Country Name'].astype(str)
merged['Country Code'] = merged['Country Code'].astype(str)
merged['Rural Value'] = merged['Rural Value'].astype(float)
merged['Electricity Value'] = merged['Electricity Value'].astype(float)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_47/target_multisource_mcts.csv", index=False)