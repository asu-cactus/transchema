import pandas as pd

# Read all source tables with index_col=0 to ignore the numerical index column
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_9.csv", index_col=0)

# UNION the dimension tables (sources with same schema)
dim_union = pd.concat([source0, source2, source3, source9], ignore_index=True)

# Join the unioned dimension table with all aspect tables on ROW_WID
# Use inner joins to keep only matching rows as in target examples

result = dim_union.merge(source1, on="ROW_WID", how="inner") \
                  .merge(source4, on="ROW_WID", how="inner") \
                  .merge(source5, on="ROW_WID", how="inner") \
                  .merge(source6, on="ROW_WID", how="inner") \
                  .merge(source7, on="ROW_WID", how="inner") \
                  .merge(source8, on="ROW_WID", how="inner")

# Group by the leftmost non-float unique columns to ensure uniqueness
# According to target schema and hints: group by CANCELED, ROW_WID, ACCNT_LOC
group_cols = ["CANCELED", "ROW_WID", "ACCNT_LOC"]

# Since no aggregation is specified, just drop duplicates by group columns keeping first
result = result.sort_values(group_cols).drop_duplicates(subset=group_cols, keep='first')

# Reorder columns to match target schema exactly
target_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
                  'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
                  'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

result = result[target_columns]

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_27/target_multisource_mcts.csv", index=False)