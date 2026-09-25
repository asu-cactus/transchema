import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_1.csv", index_col=0)

df0_melted = df0.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name'], var_name='Year', value_name='Rural Value')
df0_filtered = df0_melted[df0_melted['Indicator Name'] == 'Rural population (% of total population)']
df0_filtered = df0_filtered[['Country Name', 'Country Code', 'Year', 'Rural Value']]

df1_melted = df1.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name'], var_name='Year', value_name='Electricity Value')
df1_filtered = df1_melted[df1_melted['Indicator Name'] == 'Access to electricity (% of population)']
df1_filtered = df1_filtered[['Country Name', 'Country Code', 'Year', 'Electricity Value']]

merged = pd.merge(df0_filtered, df1_filtered, on=['Country Name', 'Country Code', 'Year'], how='outer')

merged['Year'] = merged['Year'].astype(str)
merged['Country Name'] = merged['Country Name'].astype(str)
merged['Country Code'] = merged['Country Code'].astype(str)
merged['Rural Value'] = merged['Rural Value'].astype(str)
merged['Electricity Value'] = merged['Electricity Value'].astype(str)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_34/target_multisource_mcts.csv", index=False)