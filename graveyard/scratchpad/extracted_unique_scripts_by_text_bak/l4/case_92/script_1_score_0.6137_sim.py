import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

df1_2 = pd.merge(df1, df2, on="movie_id", how="inner")

df_final = pd.merge(df1_2, df0, on="user_id", how="inner")

df_final = df_final.rename(columns={
    "genres": "genres_y",
    "genres_x": "genres_x"  # placeholder, will create below
})

df_final["gender"] = df_final["gender"].map({"M": 1, "F": 2})

df_final["genres_x"] = df_final["genres_y"].copy()  # genres_x is integer in target, but source genres are string, so we keep genres_y as string and genres_x as integer placeholder

# The target schema expects:
# ['title': string, 'user_id': int, 'movie_id_x': int, 'rating': int, 'timestamp': int,
#  'gender': int, 'age': int, 'occupation': int, 'zip': int, 'genres_x': int,
#  'movie_id_y': int, 'genres_y': string]

# movie_id_x and movie_id_y: from df1 and df2 respectively
df_final = df_final.rename(columns={
    "movie_id_x": "movie_id_x",
    "movie_id_y": "movie_id_y"
})

# But currently df_final has only one movie_id column from df1 and df2 merged on movie_id.
# To create movie_id_x and movie_id_y, we can assign:
df_final["movie_id_x"] = df_final["movie_id"]
df_final["movie_id_y"] = df_final["movie_id"]

# genres_x is integer in target but source genres are string, so we encode genres to integer codes for genres_x
df_final["genres_x"] = df_final["genres_y"].astype('category').cat.codes + 1  # +1 to avoid zero if needed

# Convert gender to int (already done)
# Convert age, occupation, zip to int (zip may have string with dash, so clean)
df_final["age"] = pd.to_numeric(df_final["age"], errors='coerce').fillna(0).astype(int)
df_final["occupation"] = pd.to_numeric(df_final["occupation"], errors='coerce').fillna(0).astype(int)
df_final["zip"] = df_final["zip"].astype(str).str.extract(r'(\d+)').fillna('0').astype(int)

# Convert rating and timestamp to int
df_final["rating"] = pd.to_numeric(df_final["rating"], errors='coerce').fillna(0).astype(int)
df_final["timestamp"] = pd.to_numeric(df_final["timestamp"], errors='coerce').fillna(0).astype(int)

# user_id to int
df_final["user_id"] = pd.to_numeric(df_final["user_id"], errors='coerce').fillna(0).astype(int)

# title is string, keep as is

# Select and reorder columns to match target schema
df_final = df_final[[
    "title",
    "user_id",
    "movie_id_x",
    "rating",
    "timestamp",
    "gender",
    "age",
    "occupation",
    "zip",
    "genres_x",
    "movie_id_y",
    "genres_y"
]]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)