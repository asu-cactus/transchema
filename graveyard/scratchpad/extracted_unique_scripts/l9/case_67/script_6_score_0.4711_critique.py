import pandas as pd

# Read all source tables with index_col=0 to ignore the numerical index column
source_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_0.csv", index_col=0)
source_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_1.csv", index_col=0)
source_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_2.csv", index_col=0)
source_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_3.csv", index_col=0)
source_4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_4.csv", index_col=0)
source_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_5.csv", index_col=0)
source_6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_6.csv", index_col=0)
source_7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_7.csv", index_col=0)
source_8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_8.csv", index_col=0)
source_9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_9.csv", index_col=0)

# UNION the dimension tables with the same schema
dim_tables = [source_2, source_3, source_4, source_9]
union_dim = pd.concat(dim_tables, ignore_index=True)

# Join the unioned dimension table with all other aspect tables on ROW_WID
# Start with union_dim
df = union_dim

# Join with Source0 (COLLECTION_EVENTS_NUM)
df = df.merge(source_0, on='ROW_WID', how='left')

# Join with Source1 (INTERACTIONS_NUM)
df = df.merge(source_1, on='ROW_WID', how='left')

# Join with Source5 (INBOUND_CALLS_NUM)
df = df.merge(source_5, on='ROW_WID', how='left')

# Join with Source6 (KEYWORDS_NUM)
df = df.merge(source_6, on='ROW_WID', how='left')

# Join with Source7 (TECHSUPPORT_NUM)
df = df.merge(source_7, on='ROW_WID', how='left')

# Join with Source8 (VISITS_NUM)
df = df.merge(source_8, on='ROW_WID', how='left')

# Now group by ['CANCELED', 'ROW_WID'] to ensure uniqueness and aggregate
# Aggregations:
# - mean for ARPU, MONTHS_AGE (float columns)
# - sum for counts: COLLECTION_EVENTS_NUM, INBOUND_CALLS_NUM, KEYWORDS_NUM, VISITS_NUM, TECHSUPPORT_NUM, INTERACTIONS_NUM, HOME_PASSED
# - For other columns that are strings or dates, take first (since they should be identical per ROW_WID)

agg_dict = {
    'ACCNT_LOC': 'first',
    'ARPU': 'mean',
    'SES': 'first',
    'HOME_PASSED': 'sum',
    'CUST_SINCE_DT': 'first',
    'MONTHS_AGE': 'mean',
    'CANCEL_DT': 'first',
    'CITY': 'first',
    'POP': 'first',
    'COLLECTION_EVENTS_NUM': 'sum',
    'INBOUND_CALLS_NUM': 'sum',
    'KEYWORDS_NUM': 'sum',
    'VISITS_NUM': 'sum',
    'TECHSUPPORT_NUM': 'sum',
    'INTERACTIONS_NUM': 'sum'
}

df_grouped = df.groupby(['CANCELED', 'ROW_WID'], as_index=False).agg(agg_dict)

# Write the final output with columns in the exact target schema order
target_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
                  'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
                  'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df_grouped = df_grouped[target_columns]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_67/target_multisource_mcts.csv", index=False)