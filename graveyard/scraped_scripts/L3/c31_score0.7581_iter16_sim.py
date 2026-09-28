import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_2.csv", index_col=0)

join_0_2 = pd.merge(source2, source0[['movie_id', 'title']], on='movie_id', how='inner')
full_join = pd.merge(join_0_2, source1[['user_id', 'gender']], on='user_id', how='inner')

f_ratings = full_join[full_join['gender'] == 'F'].groupby('title')['rating'].mean()
m_ratings = full_join[full_join['gender'] == 'M'].groupby('title')['rating'].mean()

result = pd.DataFrame({
    'title': f_ratings.index,
    'F': f_ratings.values,
    'M': m_ratings.reindex(f_ratings.index).values
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_31/target_multisource_mcts.csv", index=False)