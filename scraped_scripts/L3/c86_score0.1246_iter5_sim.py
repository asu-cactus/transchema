import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_86/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_86/training_1.csv"
source2_path = "autopipeline-benchmarks/github-pipelines/length3_86/training_2.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length3_86/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)
df2 = pd.read_csv(source2_path, index_col=0)

df0 = df0.rename(columns={"Country Name": "Country"})

id_vars = ['Country', 'Country Code', 'Indicator Name', 'Indicator Code']
value_vars = [str(y) for y in range(1960, 2016)]
df0_unpivot = df0.melt(id_vars=id_vars, value_vars=value_vars, var_name='Year', value_name='Value')

df0_unpivot['Year'] = df0_unpivot['Year'].astype(int)

pivoted = df0_unpivot.pivot_table(index=['Country', 'Country Code', 'Year'], 
                                  columns='Indicator Name', values='Value', aggfunc='first').reset_index()

pivoted.columns.name = None

pivoted = pivoted.rename(columns={
    'GDP at market prices (constant 2010 US$)': 'GDP',
})

df1 = df1.rename(columns={'Country': 'Country'})

df_merged_01 = pd.merge(pivoted, df1, how='inner', on='Country')

df_merged = pd.merge(df_merged_01, df2, how='inner', on='Country')

df_merged['Rank'] = df_merged['Rank'].astype(int)

df_merged['Documents'] = df_merged['Documents'].astype(int)
df_merged['Citable documents'] = df_merged['Citable documents'].astype(int)
df_merged['Citations'] = df_merged['Citations'].astype(int)
df_merged['Self-citations'] = df_merged['Self-citations'].astype(int)
df_merged['Citations per document'] = df_merged['Citations per document'].round().astype(int)
df_merged['H index'] = df_merged['H index'].astype(int)
df_merged['Energy Supply'] = df_merged['Energy Supply'].astype(int)
df_merged['Energy Supply per Capita'] = df_merged['Energy Supply per Capita'].astype(int)
df_merged['% Renewable'] = df_merged['% Renewable'].round().astype(int)

years = [str(y) for y in range(2006, 2016)]
for y in years:
    if y in df_merged.columns:
        df_merged[y] = df_merged[y].round().astype(int)
    else:
        df_merged[y] = pd.NA

target_cols = ['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations', 'Citations per document',
               'H index', 'Energy Supply', 'Energy Supply per Capita', '% Renewable'] + years

df_target = df_merged[target_cols]

df_target.to_csv(target_path, index=False)