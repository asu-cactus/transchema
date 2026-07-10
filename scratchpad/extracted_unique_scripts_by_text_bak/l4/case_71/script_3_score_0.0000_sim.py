import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_71/training_0.csv", index_col=0)

cols_target = ['Name', 'Age', 'G', 'MP', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'ORB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'FG%', '3P%', 'FT%', 'MP.1', 'PTS.1', 'TRB.1', 'AST.1']

df = df0[cols_target].copy()

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_71/target_multisource_mcts.csv", index=False)