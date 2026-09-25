import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_14/training_1.csv", index_col=0)

result = pd.merge(source0, source1, left_on="PLAYER", right_on="Player", how="inner")

result = result[['PLAYER', '2017-18', '#', 'Player', 'Team', 'GP', 'MPG', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'TOV', 'PF', 'ORB', 'DRB', 'RPG', 'APG', 'SPG', 'BPG', 'PPG']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_14/target_multisource_mcts.csv")