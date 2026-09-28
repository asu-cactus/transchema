import pandas as pd

# Read all source tables with index_col=0 to ignore numerical index column
source_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
source_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
source_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
source_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
source_4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
source_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
source_6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
source_7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
source_8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
source_9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

# UNION all dimension tables with same schema (Source9_34_2,5,6,8)
dim_union = pd.concat([source_2, source_5, source_6, source_8], ignore_index=True)

# Join dimension union with all aspect tables on ROW_WID
# Start with dim_union and join sequentially with each aspect table

# Join with source_0
df = pd.merge(dim_union, source_0, on="ROW_WID", how="inner")

# Join with source_1
df = pd.merge(df, source_1, on="ROW_WID", how="inner")

# Join with source_3
df = pd.merge(df, source_3, on="ROW_WID", how="inner")

# Join with source_4
df = pd.merge(df, source_4, on="ROW_WID", how="inner")

# Join with source_7
df = pd.merge(df, source_7, on="ROW_WID", how="inner")

# Join with source_9
df = pd.merge(df, source_9, on="ROW_WID", how="inner")

# Now df contains all joined data, including KEYWORDS_NUM

# Group by KEYWORDS_NUM and count occurrences to match target row count and distribution
result = df.groupby("KEYWORDS_NUM", as_index=False).size()
result.columns = ["KEYWORDS_NUM", "count"]

# The target schema only has KEYWORDS_NUM, so output only that column
# The target examples show only KEYWORDS_NUM column, so we output unique KEYWORDS_NUM values
# The count column is not in target schema, so drop it

# Output unique KEYWORDS_NUM values (one row per KEYWORDS_NUM)
# But target has 4161 rows, so likely duplicates are needed.
# The target examples show only KEYWORDS_NUM column, so output all rows with KEYWORDS_NUM values

# To produce the correct number of rows, output the KEYWORDS_NUM column from df directly
# Because the target has only KEYWORDS_NUM column, and the source_9 table has that column,
# after joining all tables, the KEYWORDS_NUM column is present with all rows.

# So final output is the KEYWORDS_NUM column from the joined dataframe

final_output = df[["KEYWORDS_NUM"]]

# Write to CSV
final_output.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)