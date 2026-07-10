import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_7/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_7/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_7/training_3.csv", index_col=0)

df0['Year'] = 2013
df1['Year'] = 2014
df2['Year'] = 2015
df3['Year'] = 2016

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

agg = df_all.groupby(['Wrestler', 'Year'], as_index=False).agg({'Wins':'sum', 'Losses':'sum', 'Draws':'sum'})

pivot = agg.pivot(index='Wrestler', columns='Year', values=['Wins', 'Losses', 'Draws'])

pivot.columns = [f"{year} {stat}" for stat, year in pivot.columns]
pivot = pivot.reset_index()

pivot = pivot.fillna(0)

int_cols = ['2013 Wins', '2013 Losses', '2013 Draws',
            '2014 Wins', '2014 Losses', '2014 Draws',
            '2015 Wins', '2015 Losses', '2015 Draws',
            '2016 Wins', '2016 Losses', '2016 Draws']

pivot[int_cols] = pivot[int_cols].astype(int)

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_7/target_multisource_mcts.csv", index=False)