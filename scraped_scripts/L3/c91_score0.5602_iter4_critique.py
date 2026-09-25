import pandas as pd
import numpy as np

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

# Convert release_date in source0 to datetime, then to float timestamp (seconds since epoch)
# If release_date is NaN or invalid, result will be NaN
source0['video_release_date'] = pd.to_datetime(source0['release_date'], errors='coerce').astype(np.int64) / 1e9
# Drop original release_date to avoid confusion
source0 = source0.drop(columns=['release_date', 'video_release_date']) \
                 .assign(video_release_date=source0['video_release_date'])

# Join source1 and source2 on user_id
joined_1_2 = source1.merge(source2, on='user_id', how='inner')

# Join the above with source0 on movie_id
joined_all = joined_1_2.merge(source0, on='movie_id', how='inner')

# Group by title and movie_id (leftmost non-float unique columns)
# Aggregate user_id, rating, unix_timestamp, age by mean
# For video_release_date, take first (all same per movie)
final = joined_all.groupby(['title', 'movie_id'], as_index=False).agg(
    user_id=('user_id', 'mean'),
    rating=('rating', 'mean'),
    unix_timestamp=('unix_timestamp', 'mean'),
    age=('age', 'mean'),
    video_release_date=('video_release_date', 'first')
)

# Reorder columns to match target schema
final = final[['title', 'movie_id', 'video_release_date', 'user_id', 'rating', 'unix_timestamp', 'age']]

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)