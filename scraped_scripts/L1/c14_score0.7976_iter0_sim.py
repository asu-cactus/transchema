import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_14/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_14/training_1.csv", index_col=0)

merged = pd.merge(df1, df0, left_on="Player", right_on="PLAYER", how="inner")

cols = ['PLAYER', '2017-18', '#', 'Player', 'Team', 'GP', 'MPG', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'TOV', 'PF', 'ORB', 'DRB', 'RPG', 'APG', 'SPG', 'BPG', 'PPG']
result = merged[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_14/target_multisource_mcts.csv", index=False)