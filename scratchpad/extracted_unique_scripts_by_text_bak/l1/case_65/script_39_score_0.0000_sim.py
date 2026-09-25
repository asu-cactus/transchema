import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="movie_id")

grouped = joined.groupby("year").size().reset_index(name='0')

grouped['year'] = grouped['year'].astype(int)
grouped['0'] = grouped['0'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)