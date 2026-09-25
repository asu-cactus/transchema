import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_2.csv", index_col=0)

# Join ratings with user info on user_id
join1 = pd.merge(df1, df0, on='user_id', how='inner')

# Join the above with movie info on movie_id
join2 = pd.merge(join1, df2, on='movie_id', how='inner')

# Convert movie_title to categorical codes for movie_title_x
join2['movie_title_x'] = join2['movie_title'].astype('category').cat.codes

# Convert year to integer for year_x (coerce errors to NaN, then fill with 0)
join2['year_x'] = pd.to_numeric(join2['year'], errors='coerce').fillna(0).astype(int)

# movie_title_y and year_y as string columns (from movie info)
join2['movie_title_y'] = join2['movie_title']
join2['year_y'] = join2['year'].astype(str)

# Convert other columns to int as per target schema
join2['age'] = join2['age'].astype(int)
join2['rating'] = join2['rating'].astype(int)
join2['timestamp'] = join2['timestamp'].astype(int)
join2['user_id'] = join2['user_id'].astype(int)
join2['movie_id'] = join2['movie_id'].astype(int)

# Map gender to integers: M=1, F=2, else 0
join2['gender'] = join2['gender'].map({'M':1, 'F':2}).fillna(0).astype(int)

# Map occupation to integer codes dynamically
occupation_codes = {occ: i+1 for i, occ in enumerate(join2['occupation'].dropna().unique())}
join2['occupation'] = join2['occupation'].map(occupation_codes).fillna(0).astype(int)

# Convert zip to int, coercing errors to 0
join2['zip'] = pd.to_numeric(join2['zip'], errors='coerce').fillna(0).astype(int)

# Select columns in the exact order and names as target schema
result = join2[['movie_id', 'movie_title_x', 'year_x', 'user_id', 'rating', 'timestamp', 'age', 'gender', 'occupation', 'zip', 'movie_title_y', 'year_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_10/target_multisource_mcts.csv", index=False)