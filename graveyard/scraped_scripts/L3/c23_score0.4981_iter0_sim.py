import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_23/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_23/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_23/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_23/training_3.csv"
]

dfs = []
for i, path in enumerate(paths):
    df = pd.read_csv(path, index_col=0)
    year = 2013 + i
    df = df.copy()
    df['Year'] = year
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby(['Wrestler', 'Year'], as_index=False).agg({'Wins':'sum', 'Losses':'sum', 'Draws':'sum'})

pivot = agg.pivot(index='Wrestler', columns='Year', values=['Wins', 'Losses', 'Draws'])

pivot.columns = [f"{stat}_{year}" for stat, year in pivot.columns]

pivot = pivot.reset_index()

pivot = pivot.rename(columns={
    'Wins_2013': '2013 Wins', 'Losses_2013': '2013 Losses', 'Draws_2013': '2013 Draws',
    'Wins_2014': '2014 Wins', 'Losses_2014': '2014 Losses', 'Draws_2014': '2014 Draws',
    'Wins_2015': '2015 Wins', 'Losses_2015': '2015 Losses', 'Draws_2015': '2015 Draws',
    'Wins_2016': '2016 Wins', 'Losses_2016': '2016 Losses', 'Draws_2016': '2016 Draws'
})

pivot = pivot.fillna(0)

pivot[['2013 Wins', '2013 Losses', '2013 Draws',
       '2014 Wins', '2014 Losses', '2014 Draws',
       '2015 Wins', '2015 Losses', '2015 Draws',
       '2016 Wins', '2016 Losses', '2016 Draws']] = pivot[[
           '2013 Wins', '2013 Losses', '2013 Draws',
           '2014 Wins', '2014 Losses', '2014 Draws',
           '2015 Wins', '2015 Losses', '2015 Draws',
           '2016 Wins', '2016 Losses', '2016 Draws']].astype(int)

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_23/target_multisource_mcts.csv", index=False)