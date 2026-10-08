import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length3_34/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length3_34/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length3_34/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

def pivot_source(df):
    id_vars = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
    value_vars = [col for col in df.columns if col not in id_vars]
    df_long = df.melt(id_vars=id_vars, value_vars=value_vars, var_name='Year', value_name='Value')
    df_long['Year'] = df_long['Year'].astype(str)
    df_pivot = df_long.pivot_table(index=['Country Name', 'Country Code', 'Year'], 
                                   columns='Indicator Name', values='Value', aggfunc='first').reset_index()
    return df_pivot

pivoted_0 = pivot_source(df0)
pivoted_1 = pivot_source(df1)

# Join on Country Name, Country Code, Year to combine indicators side-by-side
merged = pd.merge(pivoted_0, pivoted_1, on=['Country Name', 'Country Code', 'Year'], how='inner')

result = merged.rename(columns={
    'Rural population (% of total population)': 'Rural Value',
    'Access to electricity (% of population)': 'Electricity Value'
})

result = result[['Country Name', 'Country Code', 'Year', 'Rural Value', 'Electricity Value']]

result.to_csv(target_path, index=False)