import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/training_4.csv", index_col=0)

join_result = pd.merge(s3, s1, how='inner', on=['Year', 'Category'], suffixes=('_3', '_1'))

union_0_2_4 = pd.concat([s0, s2, s4], ignore_index=True)

# The join_result has duplicated columns Nominee, Movie, Winner from both tables with suffixes.
# We need to unify columns to match target schema: Year, Category, Nominee, Movie, Winner
# The target schema has single columns for Nominee, Movie, Winner.
# We will take Nominee_3, Movie_3, Winner_3 from s3 side (join left), and drop the s1 side columns.

join_result_clean = join_result[['Year', 'Category', 'Nominee_3', 'Movie_3', 'Winner_3']]
join_result_clean.columns = ['Year', 'Category', 'Nominee', 'Movie', 'Winner']

final_df = pd.concat([join_result_clean, union_0_2_4], ignore_index=True)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_66/target_multisource_mcts.csv", index=False)