import pandas as pd

# Read all source CSVs with index_col=0 as per Hint 22
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_9.csv", index_col=0)

# UNION the dimension tables (same schema)
dim_tables = [src0, src2, src4, src9]
dim_union = pd.concat(dim_tables, ignore_index=True)

# Join the unioned dimension table with all aspect tables on ROW_WID
# Start with dim_union
df = dim_union

# Join with Source9_68_1 (TECHSUPPORT_NUM)
df = df.merge(src1, on='ROW_WID', how='inner')

# Join with Source9_68_3 (VISITS_NUM)
df = df.merge(src3, on='ROW_WID', how='inner')

# Join with Source9_68_5 (KEYWORDS_NUM)
df = df.merge(src5, on='ROW_WID', how='inner')

# Join with Source9_68_6 (INBOUND_CALLS_NUM)
df = df.merge(src6, on='ROW_WID', how='inner')

# Join with Source9_68_7 (INTERACTIONS_NUM)
df = df.merge(src7, on='ROW_WID', how='inner')

# Join with Source9_68_8 (COLLECTION_EVENTS_NUM)
df = df.merge(src8, on='ROW_WID', how='inner')

# Group by the leftmost non-float unique columns to remove duplicates
# According to target schema and hints, group by ['CANCELED', 'ROW_WID', 'ACCNT_LOC']
group_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC']

# Since no aggregation is specified, just drop duplicates by grouping and taking first
df = df.groupby(group_cols, as_index=False).first()

# Reorder columns to match target schema exactly
target_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
                  'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
                  'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df[target_columns]

# Write output CSV
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_68/target_multisource_mcts.csv", index=False)