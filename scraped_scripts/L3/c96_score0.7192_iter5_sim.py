import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_2.csv", index_col=0)

df = source2.merge(source1, on="movie id", how="left")
df = df.merge(source0, on="user id", how="left")

df["release date"] = pd.to_datetime(df["release date"], errors='coerce').dt.year.fillna(0).astype(int)
df["video release date"] = pd.to_datetime(df["video release date"], errors='coerce').dt.year.fillna(0).astype(int)
df["IMDb URL"] = df["IMDb URL"].apply(lambda x: 0 if pd.isna(x) else len(str(x)))
df["Romance "] = df["Romance "].fillna(0).astype(int)

cols_int = ['movie id', 'release date', 'video release date', 'IMDb URL', 'unknown', 'Action', 'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance ', 'Sci-Fi', 'Thriller', 'War', 'Western', 'user id', 'rating', 'timestamp', 'age', 'occupation']
for c in cols_int:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)

df["gender"] = df["gender"].map({"M": 1, "F": 0}).fillna(0).astype(int)

target_cols = ['movie title', 'movie id', 'release date', 'video release date', 'IMDb URL', 'unknown', 'Action', 'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance ', 'Sci-Fi', 'Thriller', 'War', 'Western', 'user id', 'rating', 'timestamp', 'age', 'gender', 'occupation', 'zip code']

df = df[target_cols]

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_96/target_multisource_mcts.csv", index=False)