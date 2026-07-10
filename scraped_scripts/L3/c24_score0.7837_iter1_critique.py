import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_24/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_24/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_24/training_2.csv", index_col=0)

# Join ratings with users on user_id
joined_0 = pd.merge(source2, source0, on="user_id", how="inner")

# Join the above with movies on movie_id
joined_1 = pd.merge(joined_0, source1, on="movie_id", how="inner")

# Group by title and gender, aggregate mean rating
grouped = joined_1.groupby(['title', 'gender'], as_index=False)['rating'].mean()

# Pivot to get columns 'F' and 'M'
pivoted = grouped.pivot(index='title', columns='gender', values='rating')

# Reset index to get 'title' as a column
result = pivoted.reset_index()

# Ensure columns are exactly ['title', 'F', 'M']
# Some titles may have only one gender rating, so columns may be missing
# Add missing columns if necessary
for gender_col in ['F', 'M']:
    if gender_col not in result.columns:
        result[gender_col] = pd.NA

# Reorder columns
result = result[['title', 'F', 'M']]

# Left join with all titles to ensure all titles appear
result = pd.merge(source1[['title']], result, on='title', how='left')

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_24/target_multisource_mcts.csv", index=False)