import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)
agg = df0.groupby("year").agg({'movie_id':'count'}).reset_index()
agg.columns = ['year', '0']
agg['year'] = agg['year'].astype(int)
agg['0'] = agg['0'].astype(int)
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)