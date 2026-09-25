import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

agg = df0.groupby('doggo', dropna=False).agg(dog_type=('tweet_id', 'count')).reset_index()

agg['dog_type'] = agg['dog_type'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)