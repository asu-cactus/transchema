import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_62/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_62/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_62/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_62/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['Year'] = df.groupby('Wrestler').cumcount() + 2013
df_pivot = df.pivot(index='Wrestler', columns='Year', values=['Wins', 'Losses', 'Draws'])

df_pivot.columns = [f"{year} {metric}" for metric, year in df_pivot.columns]
df_pivot = df_pivot.reset_index()

int_cols = [col for col in df_pivot.columns if col != 'Wrestler']
df_pivot[int_cols] = df_pivot[int_cols].fillna(0).astype(int)

df_pivot = df_pivot[['Wrestler',
                     '2013 Wins', '2013 Losses', '2013 Draws',
                     '2014 Wins', '2014 Losses', '2014 Draws',
                     '2015 Wins', '2015 Losses', '2015 Draws',
                     '2016 Wins', '2016 Losses', '2016 Draws']]

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_62/target_multisource_mcts.csv", index=False)