import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_3.csv", index_col=0)

df0['Year'] = 2013
df1['Year'] = 2014
df2['Year'] = 2015
df3['Year'] = 2016

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_pivot = df.melt(id_vars=['Wrestler', 'Year'], value_vars=['Wins', 'Losses', 'Draws'], var_name='Result', value_name='Count')
df_pivot = df_pivot.pivot_table(index='Wrestler', columns=['Year', 'Result'], values='Count', aggfunc='sum')

df_pivot.columns = [f"{year} {result}" for year, result in df_pivot.columns]
df_pivot = df_pivot.reset_index()

int_cols = df_pivot.columns.drop('Wrestler')
df_pivot[int_cols] = df_pivot[int_cols].fillna(0).astype(int)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_1/target_multisource_mcts.csv", index=False)