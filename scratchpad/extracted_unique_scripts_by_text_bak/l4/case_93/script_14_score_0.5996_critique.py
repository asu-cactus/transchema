import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

# Join ratings with user info on user_id
join_0_2 = pd.merge(source2, source0, on="user_id", how="inner")

# Join with movie info first time (for title_x, genres_x)
join_1 = pd.merge(join_0_2, source1, on="movie_id", how="inner", suffixes=('_x', '_y'))

# Join with movie info second time (for title_y, genres_y)
# To get the second set of movie columns, join again with source1 but rename columns to avoid collision
# We rename columns of source1 before join to avoid suffix issues
source1_renamed = source1.rename(columns={"title": "title_y", "genres": "genres_y"})

final_join = pd.merge(join_1, source1_renamed, on="movie_id", how="inner")

# Construct final DataFrame with exact target schema and types
final = pd.DataFrame()

final["movie_id"] = final_join["movie_id"].astype("Int64")
final["user_id"] = final_join["user_id"].astype("Int64")
final["rating"] = final_join["rating"].astype("Int64")
final["timestamp"] = final_join["timestamp"].astype("Int64")

def gender_to_int(g):
    if pd.isna(g):
        return pd.NA
    g = str(g).strip().upper()
    if g == "M":
        return 2
    elif g == "F":
        return 6
    else:
        return pd.NA

final["gender"] = final_join["gender"].map(gender_to_int).astype("Int64")

def to_int_or_na(x):
    try:
        return int(str(x).split('-')[0])
    except:
        return pd.NA

final["age"] = final_join["age"].map(to_int_or_na).astype("Int64")
final["occupation"] = final_join["occupation"].map(to_int_or_na).astype("Int64")
final["zip"] = final_join["zip"].map(to_int_or_na).astype("Int64")

# title_x and genres_x: length of strings from first movie join (suffix _x)
final["title_x"] = final_join["title_x"].str.len().astype("Int64")
final["genres_x"] = final_join["genres_x"].str.len().astype("Int64")

# title_y and genres_y: strings from second movie join (already renamed)
final["title_y"] = final_join["title_y"].astype("string")
final["genres_y"] = final_join["genres_y"].astype("string")

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)