import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_71/training_0.csv", index_col=0)

agg_funcs = {
    'Age': 'mean',
    'G': 'sum',
    'MP': 'sum',
    'FG': 'sum',
    'FGA': 'sum',
    '3P': 'sum',
    '3PA': 'sum',
    'FT': 'sum',
    'FTA': 'sum',
    'ORB': 'sum',
    'TRB': 'sum',
    'AST': 'sum',
    'STL': 'sum',
    'BLK': 'sum',
    'TOV': 'sum',
    'PF': 'sum',
    'PTS': 'sum',
    'FG%': 'mean',
    '3P%': 'mean',
    'FT%': 'mean',
    'MP.1': 'sum',
    'PTS.1': 'sum',
    'TRB.1': 'sum',
    'AST.1': 'sum'
}

grouped = df0.groupby('Name', as_index=False).agg(agg_funcs)

grouped = grouped[['Name', 'Age', 'G', 'MP', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'ORB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'FG%', '3P%', 'FT%', 'MP.1', 'PTS.1', 'TRB.1', 'AST.1']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_71/target_multisource_mcts.csv", index=False)