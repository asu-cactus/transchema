import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)

grouped = df0.groupby("year").agg({'movie_id': 'count'}).reset_index()

grouped.columns = ['year', '0']

grouped['year'] = grouped['year'].astype(int)
grouped['0'] = grouped['0'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)