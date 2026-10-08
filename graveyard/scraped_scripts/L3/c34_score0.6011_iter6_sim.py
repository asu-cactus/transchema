import pandas as pd

rural = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_0.csv", index_col=0)
elec = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_1.csv", index_col=0)

rural_melt = rural.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], var_name='Year', value_name='Rural Value')
elec_melt = elec.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], var_name='Year', value_name='Electricity Value')

merged = pd.merge(rural_melt, elec_melt,
                  on=['Country Name', 'Country Code', 'Year'],
                  how='outer')

result = merged[['Country Name', 'Country Code', 'Year', 'Rural Value', 'Electricity Value']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_34/target_multisource_mcts.csv", index=False)