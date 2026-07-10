import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_1.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

years = [str(y) for y in range(1960, 2018)]
df_melt = df.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name'], value_vars=years, var_name='Year', value_name='Value')

df_pivot = df_melt.pivot_table(index=['Country Name', 'Country Code', 'Year'], columns='Indicator Name', values='Value', aggfunc='mean')

df_pivot = df_pivot.rename(columns={
    'Rural population (% of total population)': 'Rural Value',
    'Access to electricity (% of population)': 'Electricity Value'
})

df_pivot = df_pivot.reset_index()

for col in ['Country Name', 'Country Code', 'Year', 'Rural Value', 'Electricity Value']:
    df_pivot[col] = df_pivot[col].astype(str)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_34/target_multisource_mcts.csv", index=False)