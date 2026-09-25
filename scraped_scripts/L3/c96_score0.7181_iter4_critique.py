import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_2.csv", index_col=0)

# Join Source2 (ratings) with Source0 (users) on 'user id'
join_20 = pd.merge(source2, source0, how='inner', on='user id')

# Join the above result with Source1 (movies) on 'movie id'
final_join = pd.merge(join_20, source1, how='inner', on='movie id')

# Convert columns to match target schema and types
final_join['movie title'] = final_join['movie title'].astype(str)
final_join['movie id'] = final_join['movie id'].astype(int)

final_join['release date'] = pd.to_datetime(final_join['release date'], errors='coerce').dt.year.fillna(0).astype(int)
final_join['video release date'] = pd.to_datetime(final_join['video release date'], errors='coerce').dt.year.fillna(0).astype(int)

# Convert IMDb URL to integer indicator (0 if NaN, else 1)
final_join['IMDb URL'] = final_join['IMDb URL'].apply(lambda x: 0 if pd.isna(x) else 1).astype(int)

genre_cols = ['unknown', 'Action', 'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime', 'Documentary',
              'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance ', 'Sci-Fi', 'Thriller',
              'War', 'Western']

for col in genre_cols:
    if col in final_join.columns:
        final_join[col] = final_join[col].fillna(0).astype(int)
    else:
        final_join[col] = 0

final_join['user id'] = final_join['user id'].astype(int)
final_join['rating'] = final_join['rating'].astype(int)
final_join['timestamp'] = final_join['timestamp'].astype(int)
final_join['age'] = final_join['age'].astype(int)
final_join['gender'] = final_join['gender'].map({'M': 1, 'F': 0}).fillna(0).astype(int)
final_join['occupation'] = final_join['occupation'].astype('category').cat.codes
final_join['zip code'] = final_join['zip code'].astype('category').cat.codes

final = final_join[['movie title', 'movie id', 'release date', 'video release date', 'IMDb URL'] + genre_cols +
                   ['user id', 'rating', 'timestamp', 'age', 'gender', 'occupation', 'zip code']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_96/target_multisource_mcts.csv", index=False)