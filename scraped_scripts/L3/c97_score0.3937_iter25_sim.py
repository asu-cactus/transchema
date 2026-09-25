import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_2.csv", index_col=0)

genre_cols = ['Action', 'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance ', 'Sci-Fi', 'Thriller', 'War', 'Western']
unpivoted = source0.melt(id_vars=['movie id', 'movie title'], value_vars=genre_cols, var_name='genre', value_name='genre_flag')

joined_1 = pd.merge(unpivoted, source2, on='movie id', how='inner')
joined_2 = pd.merge(joined_1, source1, on='user id', how='inner')

result = joined_2[['movie title', 'rating']].copy()
result['rating'] = result['rating'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_97/target_multisource_mcts.csv", index=False)