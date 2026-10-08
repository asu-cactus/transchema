import pandas as pd

# Read all source tables with index_col=0
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_9.csv", index_col=0)

# UNION the dimension tables (same schema)
dim_tables = [source0, source2, source6, source7]
unioned_dim = pd.concat(dim_tables, ignore_index=True)

# Join the unioned dimension table with all aspect tables on ROW_WID
# Start with unioned_dim
df = unioned_dim

# Join with Source1 (KEYWORDS_NUM)
df = df.merge(source1, on="ROW_WID", how="inner")

# Join with Source3 (VISITS_NUM)
df = df.merge(source3, on="ROW_WID", how="inner")

# Join with Source4 (COLLECTION_EVENTS_NUM)
df = df.merge(source4, on="ROW_WID", how="inner")

# Join with Source5 (TECHSUPPORT_NUM)
df = df.merge(source5, on="ROW_WID", how="inner")

# Join with Source8 (INBOUND_CALLS_NUM)
df = df.merge(source8, on="ROW_WID", how="inner")

# Join with Source9 (INTERACTIONS_NUM)
df = df.merge(source9, on="ROW_WID", how="inner")

# Reorder columns to match target schema exactly
target_columns = [
    'CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED',
    'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
    'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM',
    'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM'
]

df = df[target_columns]

# Write to target CSV
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts.csv", index=False)