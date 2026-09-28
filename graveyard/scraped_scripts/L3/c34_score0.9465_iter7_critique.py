import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_1.csv", index_col=0)

df0_melted = df0.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name'], 
                      var_name='Year', value_name='Rural Value')
df1_melted = df1.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name'], 
                      var_name='Year', value_name='Electricity Value')

df0_rural = df0_melted[df0_melted['Indicator Name'] == 'Rural population (% of total population)']
df1_elec = df1_melted[df1_melted['Indicator Name'] == 'Access to electricity (% of population)']

df_joined = pd.merge(df0_rural[['Country Name', 'Country Code', 'Year', 'Rural Value']],
                     df1_elec[['Country Name', 'Country Code', 'Year', 'Electricity Value']],
                     on=['Country Name', 'Country Code', 'Year'], how='inner')

df_joined = df_joined[['Country Name', 'Country Code', 'Year', 'Rural Value', 'Electricity Value']]

df_joined.to_csv("autopipeline-benchmarks/github-pipelines/length3_34/target_multisource_mcts.csv", index=False)