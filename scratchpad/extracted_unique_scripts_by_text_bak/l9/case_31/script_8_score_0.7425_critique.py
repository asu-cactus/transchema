import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_1.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_3.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_5.csv", index_col=0)

df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_2.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_4.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_9.csv", index_col=0)

# Join the four large tables on ROW_WID using outer joins to keep all rows
join01 = pd.merge(df0, df1, on="ROW_WID", how="outer", suffixes=('_0', '_1'))
join013 = pd.merge(join01, df3, on="ROW_WID", how="outer", suffixes=('', '_3'))
join0135 = pd.merge(join013, df5, on="ROW_WID", how="outer", suffixes=('', '_5'))

# Join with other tables on ROW_WID using left joins to keep all rows from main dimension
join_all = join0135.merge(df2, on="ROW_WID", how="left") \
                   .merge(df4, on="ROW_WID", how="left") \
                   .merge(df6, on="ROW_WID", how="left") \
                   .merge(df7, on="ROW_WID", how="left") \
                   .merge(df8, on="ROW_WID", how="left") \
                   .merge(df9, on="ROW_WID", how="left")

# Coalesce HOME_PASSED columns from the four large tables
# Columns: HOME_PASSED_0 (from df0), HOME_PASSED_1 (from df1), HOME_PASSED (from df3), HOME_PASSED_5 (from df5)
# After merges, columns are named:
# 'HOME_PASSED_0', 'HOME_PASSED_1', 'HOME_PASSED', 'HOME_PASSED_5'

# Create a HOME_PASSED column by taking first non-null value among these columns
home_passed_cols = ['HOME_PASSED_0', 'HOME_PASSED_1', 'HOME_PASSED', 'HOME_PASSED_5']
join_all['HOME_PASSED'] = join_all[home_passed_cols].bfill(axis=1).iloc[:, 0]

# Select only HOME_PASSED column
result = join_all[['HOME_PASSED']].copy()

# Convert to integer type with nullable Int64 dtype
result['HOME_PASSED'] = result['HOME_PASSED'].astype('Int64')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)