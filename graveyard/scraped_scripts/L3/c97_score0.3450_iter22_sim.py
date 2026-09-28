import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_0.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_2.csv", index_col=0)

id_vars = ['movie id', 'movie title', 'release date', 'video release date', 'IMDb URL']
value_vars = ['unknown', 'Action', 'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance ', 'Sci-Fi', 'Thriller', 'War', 'Western']

unpivot = source0.melt(id_vars=id_vars, value_vars=value_vars, var_name='genre', value_name='value')

joined = pd.merge(unpivot, source2, how='inner', left_on='movie id', right_on='movie id')

result = joined[['movie title', 'rating']].copy()
result['rating'] = result['rating'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_97/target_multisource_mcts.csv", index=False)