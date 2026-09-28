import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_2.csv", index_col=0)

# Join ratings with movies on 'movie id'
merged_1_2 = pd.merge(source2, source1, on="movie id", how="inner")

# Join the above with users on 'user id'
final = pd.merge(merged_1_2, source0, on="user id", how="inner")

# Convert string columns to categorical codes to match integer target schema
# Columns from source1: 'release date', 'video release date', 'IMDb URL'
for col in ['release date', 'video release date', 'IMDb URL']:
    final[col] = final[col].astype('category').cat.codes

# Columns from source0: 'gender', 'occupation'
for col in ['gender', 'occupation']:
    final[col] = final[col].astype('category').cat.codes

# Select columns in exact order as target schema
final = final[[
    "movie title", "movie id", "release date", "video release date", "IMDb URL", "unknown", "Action", "Adventure",
    "Animation", "Childrens", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical",
    "Mystery", "Romance ", "Sci-Fi", "Thriller", "War", "Western", "user id", "rating", "timestamp", "age", "gender",
    "occupation", "zip code"
]]

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length3_96/target_multisource_mcts.csv", index=False)