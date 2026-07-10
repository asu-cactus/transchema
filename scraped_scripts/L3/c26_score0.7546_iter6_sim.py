import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_1.csv", index_col=0)

grouped = source0.merge(source1[['movie_id', 'title']], on='movie_id', how='inner')
agg = grouped.groupby('title', as_index=False).agg({'user_id':'count'})
agg.rename(columns={'user_id':'0'}, inplace=True)
agg['0'] = agg['0'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_26/target_multisource_mcts.csv", index=False)