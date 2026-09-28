import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['Year'] = df_all.groupby('Wrestler').cumcount() + 2013

df_melted = df_all.melt(id_vars=['Wrestler', 'Year'], value_vars=['Wins', 'Losses', 'Draws'], var_name='Stat', value_name='Value')

df_pivot = df_melted.pivot_table(index='Wrestler', columns=['Year', 'Stat'], values='Value', aggfunc='first')

df_pivot.columns = [f"{year} {stat}" for year, stat in df_pivot.columns]

df_pivot = df_pivot.reset_index()

cols = ['Wrestler']
for year in range(2013, 2017):
    for stat in ['Wins', 'Losses', 'Draws']:
        col = f"{year} {stat}"
        if col not in df_pivot.columns:
            df_pivot[col] = pd.NA
        cols.append(col)

df_final = df_pivot[cols]

df_final[['2013 Wins', '2013 Losses', '2013 Draws',
          '2014 Wins', '2014 Losses', '2014 Draws',
          '2015 Wins', '2015 Losses', '2015 Draws',
          '2016 Wins', '2016 Losses', '2016 Draws']] = df_final[[
    '2013 Wins', '2013 Losses', '2013 Draws',
    '2014 Wins', '2014 Losses', '2014 Draws',
    '2015 Wins', '2015 Losses', '2015 Draws',
    '2016 Wins', '2016 Losses', '2016 Draws']].fillna(0).astype(int)

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_63/target_multisource_mcts.csv", index=False)