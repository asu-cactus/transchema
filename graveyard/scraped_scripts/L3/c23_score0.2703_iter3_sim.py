import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['Year'] = df_all.groupby('Wrestler').cumcount() + 2013

df_melt = df_all.melt(id_vars=['Wrestler', 'Year'], value_vars=['Wins', 'Losses', 'Draws'], var_name='Result', value_name='Count')

df_pivot = df_melt.pivot_table(index='Wrestler', columns=['Year', 'Result'], values='Count', aggfunc='sum')

df_pivot.columns = [f"{year} {result}" for year, result in df_pivot.columns]

df_pivot = df_pivot.reset_index()

cols = ['Wrestler']
for year in range(2013, 2017):
    for result in ['Wins', 'Losses', 'Draws']:
        col = f"{year} {result}"
        if col not in df_pivot.columns:
            df_pivot[col] = 0
        cols.append(col)

df_pivot = df_pivot[cols]

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_23/target_multisource_mcts.csv", index=False)