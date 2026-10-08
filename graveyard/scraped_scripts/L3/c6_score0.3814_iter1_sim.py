import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_2.csv", index_col=0)

id_vars = ['movie id', 'movie title', 'release date', 'video release date', 'IMDb URL']
value_vars = ['unknown', 'Action', 'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance ', 'Sci-Fi', 'Thriller', 'War', 'Western']

unpivoted = source1.melt(id_vars=id_vars, value_vars=value_vars, var_name='genre', value_name='value')

merged = pd.merge(unpivoted, source2, on='movie id')

filtered = merged[merged['value'] == 1]

result = filtered[['movie title', 'rating']].copy()
result['rating'] = result['rating'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_6/target_multisource_mcts.csv", index=False)