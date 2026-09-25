import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
source1_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
source1_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

union_result = pd.concat([source1_0, source1_1], ignore_index=True)

join_result_1 = pd.merge(union_result, source2, on="movie_id", how="inner")

final_join = pd.merge(join_result_1, source0, on="user_id", how="inner")

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

final["title_x"] = final_join["title"].str.len().astype("Int64")
final["genres_x"] = final_join["genres"].str.len().astype("Int64")

final["title_y"] = final_join["title"].astype("string")
final["genres_y"] = final_join["genres"].astype("string")

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)