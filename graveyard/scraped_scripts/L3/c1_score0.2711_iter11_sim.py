import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['Year'] = df_all.groupby('Wrestler').cumcount() + 2013

df_melted = df_all.melt(id_vars=['Wrestler', 'Year'], value_vars=['Wins', 'Losses', 'Draws'], var_name='Stat', value_name='Value')

df_pivot = df_melted.pivot_table(index='Wrestler', columns=['Year', 'Stat'], values='Value', aggfunc='sum')

df_pivot.columns = [f"{year} {stat}" for year, stat in df_pivot.columns]

df_pivot = df_pivot.reset_index()

cols_order = ['Wrestler']
for year in range(2013, 2017):
    for stat in ['Wins', 'Losses', 'Draws']:
        col = f"{year} {stat}"
        if col in df_pivot.columns:
            cols_order.append(col)

df_pivot = df_pivot[cols_order]

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_1/target_multisource_mcts.csv", index=False)