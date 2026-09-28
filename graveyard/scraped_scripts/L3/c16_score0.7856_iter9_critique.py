import pandas as pd
import numpy as np

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_2.csv", index_col=0)

# Join Source0 and Source1 on user_id
join_0_1 = pd.merge(source0, source1, on="user_id", how="inner")

# Join the above result with Source2 on movie_id
full_join = pd.merge(join_0_1, source2, on="movie_id", how="inner")

# Create gender-specific rating columns, fill other gender ratings with 0 for correct mean calculation
full_join['F_rating'] = np.where(full_join['gender'] == 'F', full_join['rating'], 0)
full_join['M_rating'] = np.where(full_join['gender'] == 'M', full_join['rating'], 0)

# Group by title and calculate mean ratings for F and M
result = full_join.groupby('title').agg(
    F=('F_rating', 'mean'),
    M=('M_rating', 'mean')
).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_16/target_multisource_mcts.csv", index=False)