import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_43/training_1.csv", index_col=0)

agg_cols = ['speechiness', 'instrumentalness', 'danceability', 'energy', 'acousticness']

grouped_0 = df0.groupby('artist_name')[agg_cols].min().reset_index()
grouped_1 = df1.groupby('artist_name')[agg_cols].min().reset_index()

concat_df = pd.concat([grouped_0, grouped_1], ignore_index=True)

final_df = concat_df.groupby('artist_name')[agg_cols].min().reset_index()

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_43/target_multisource_mcts.csv", index=False)