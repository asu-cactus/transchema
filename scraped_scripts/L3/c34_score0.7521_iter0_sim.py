import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_1.csv", index_col=0)

id_cols = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
value_vars = [col for col in df0.columns if col not in id_cols]

df0_melted = df0.melt(id_vars=id_cols, value_vars=value_vars, var_name='Year', value_name='Rural Value')
df1_melted = df1.melt(id_vars=id_cols, value_vars=value_vars, var_name='Year', value_name='Electricity Value')

df0_melted = df0_melted.drop(columns=['Indicator Code', 'Indicator Name'])
df1_melted = df1_melted.drop(columns=['Indicator Code', 'Indicator Name'])

df_merged = pd.merge(df0_melted, df1_melted, on=['Country Name', 'Country Code', 'Year'], how='inner')

df_merged = df_merged[['Country Name', 'Country Code', 'Year', 'Rural Value', 'Electricity Value']]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_34/target_multisource_mcts.csv", index=False)