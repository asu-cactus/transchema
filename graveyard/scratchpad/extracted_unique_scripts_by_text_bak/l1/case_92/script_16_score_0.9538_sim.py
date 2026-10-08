import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)

joined = pd.merge(df0, df0, on="user_id", suffixes=('_left', '_right'))

grouped = joined.groupby("user_id").agg({
    'email_left': 'first',
    'geo_left': 'first'
}).reset_index()

grouped.rename(columns={'email_left': 'email', 'geo_left': 'geo'}, inplace=True)

grouped['user_id'] = grouped['user_id'].astype(str)
grouped['email'] = grouped['email'].astype(str)
grouped['geo'] = grouped['geo'].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)