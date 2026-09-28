import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_8/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_8/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_8/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_8/training_3.csv"
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

pivot_wins = agg.pivot(index='Wrestler', columns='Year', values='Wins')
pivot_losses = agg.pivot(index='Wrestler', columns='Year', values='Losses')
pivot_draws = agg.pivot(index='Wrestler', columns='Year', values='Draws')

result = pd.DataFrame(index=pivot_wins.index)
for year in [2013, 2014, 2015, 2016]:
    result[f'{year} Wins'] = pivot_wins.get(year)
    result[f'{year} Losses'] = pivot_losses.get(year)
    result[f'{year} Draws'] = pivot_draws.get(year)

result.reset_index(inplace=True)

result = result.astype({
    '2013 Wins': 'Int64', '2013 Losses': 'Int64', '2013 Draws': 'Int64',
    '2014 Wins': 'Int64', '2014 Losses': 'Int64', '2014 Draws': 'Int64',
    '2015 Wins': 'Int64', '2015 Losses': 'Int64', '2015 Draws': 'Int64',
    '2016 Wins': 'Int64', '2016 Losses': 'Int64', '2016 Draws': 'Int64'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_8/target_multisource_mcts.csv", index=False)