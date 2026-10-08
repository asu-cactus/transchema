import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_1.csv", index_col=0)

agg = df1.groupby(['city', 'ride_id'], as_index=False)['fare'].mean()

agg['fare'] = agg['fare'].astype(float)
agg['ride_id'] = agg['ride_id'].astype(int)
agg['city'] = agg['city'].astype(str)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_88/target_multisource_mcts.csv", index=False)