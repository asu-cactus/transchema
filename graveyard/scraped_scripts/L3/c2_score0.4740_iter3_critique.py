import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_2.csv", index_col=0)

joined_0 = pd.merge(source0, source1[['movie_id', 'title']], on='movie_id', how='inner')
joined_1 = pd.merge(joined_0, source2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

agg = joined_1.groupby(['title', 'user_id', 'movie_id'], as_index=False).agg({
    'age': 'mean',
    'occupation': 'mean',
    'rating': 'mean',
    'timestamp': 'mean'
})

# Add the group by columns back to the dataframe (already present as group keys)
# Reorder columns to match target schema
agg = agg[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_2/target_multisource_mcts.csv", index=False)