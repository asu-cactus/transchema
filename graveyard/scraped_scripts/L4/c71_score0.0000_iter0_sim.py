import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_71/training_0.csv", index_col=0)

agg_cols = ['Age', 'G', 'MP', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'ORB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 
            'FG%', '3P%', 'FT%', 'MP.1', 'PTS.1', 'TRB.1', 'AST.1']

grouped = df0.groupby('Name', as_index=False)[agg_cols].mean()

cols_order = ['Name', 'Age', 'G', 'MP', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'ORB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 
              'FG%', '3P%', 'FT%', 'MP.1', 'PTS.1', 'TRB.1', 'AST.1']

result = grouped[cols_order]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_71/target_multisource_mcts.csv", index=False)