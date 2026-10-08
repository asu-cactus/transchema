import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_2.csv", index_col=0)

# Join ratings with user info on user_id
merged_0_2 = pd.merge(source0, source2, on="user_id", how="inner")

# Group by movie_id and gender, aggregate average rating
agg = merged_0_2.groupby(["movie_id", "gender"], as_index=False)["rating"].mean()

# Pivot gender to columns F and M
pivot = agg.pivot(index="movie_id", columns="gender", values="rating").reset_index()

# Rename columns to match target schema
pivot = pivot.rename(columns={"F": "F", "M": "M"})

# Join with movie titles (left join to keep all movies)
result = pd.merge(source1[["movie_id", "title"]], pivot, on="movie_id", how="left")

# Select final columns
final_df = result[["title", "F", "M"]]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_17/target_multisource_mcts.csv", index=False)