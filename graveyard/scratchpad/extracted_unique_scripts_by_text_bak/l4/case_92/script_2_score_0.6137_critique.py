import pandas as pd

# Read source files with index_col=0 to ignore the first index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

# Join Source1 and Source2 on movie_id
df1_2 = pd.merge(df1, df2, on="movie_id", how="inner")

# Join the above with Source0 on user_id
df_final = pd.merge(df1_2, df0, on="user_id", how="inner")

# Map gender to integer as per target schema: M->1, F->2
df_final["gender"] = df_final["gender"].map({"M": 1, "F": 2})

# Encode genres_x as integer codes from genres_y (genres from Source2)
df_final["genres_y"] = df_final["genres"]  # genres_y is string genres from Source2
df_final["genres_x"] = df_final["genres_y"].astype('category').cat.codes + 1  # +1 to avoid zero

# Rename movie_id columns to movie_id_x and movie_id_y as per target schema
# movie_id_x from Source1 (ratings), movie_id_y from Source2 (movie info)
df_final = df_final.rename(columns={
    "movie_id": "movie_id_x",  # from df1 (ratings)
    "movie_id": "movie_id_x"   # redundant but explicit
})
df_final["movie_id_y"] = df_final["movie_id_x"]  # since joined on movie_id, both are same

# Clean and convert columns to proper types
df_final["age"] = pd.to_numeric(df_final["age"], errors='coerce').fillna(0).astype(int)
df_final["occupation"] = pd.to_numeric(df_final["occupation"], errors='coerce').fillna(0).astype(int)
df_final["zip"] = df_final["zip"].astype(str).str.extract(r'(\d+)').fillna('0').astype(int)

df_final["rating"] = pd.to_numeric(df_final["rating"], errors='coerce').fillna(0).astype(int)
df_final["timestamp"] = pd.to_numeric(df_final["timestamp"], errors='coerce').fillna(0).astype(int)
df_final["user_id"] = pd.to_numeric(df_final["user_id"], errors='coerce').fillna(0).astype(int)

# Select and reorder columns to match target schema exactly
df_final = df_final[[
    "title",        # from Source2
    "user_id",      # from Source0/Source1
    "movie_id_x",   # from Source1
    "rating",       # from Source1
    "timestamp",    # from Source1
    "gender",       # mapped from Source0
    "age",          # from Source0
    "occupation",   # from Source0
    "zip",          # from Source0 cleaned
    "genres_x",     # encoded integer genres from Source2
    "movie_id_y",   # from Source2 (same as movie_id_x)
    "genres_y"      # string genres from Source2
]]

# Write output to target file
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)