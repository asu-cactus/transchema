import pandas as pd
import numpy as np

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_2.csv", index_col=0)

# Join ratings with users on user_id (inner join to keep only valid ratings with user info)
join_2_1 = pd.merge(source2, source1, on="user_id", how="inner")

# Join the above with movies on movie_id (left join to keep all movies)
join_all = pd.merge(join_2_1, source0, on="movie_id", how="right")

# Create gender-specific rating columns
join_all['F_rating'] = np.where(join_all['gender'] == 'F', join_all['rating'], np.nan)
join_all['M_rating'] = np.where(join_all['gender'] == 'M', join_all['rating'], np.nan)

# Group by title and compute mean ratings by gender
result = join_all.groupby('title').agg(F=('F_rating', 'mean'), M=('M_rating', 'mean')).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_15/target_multisource_mcts.csv", index=False)