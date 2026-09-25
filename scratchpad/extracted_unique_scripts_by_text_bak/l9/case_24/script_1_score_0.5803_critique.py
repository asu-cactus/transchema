import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_9.csv", index_col=0)

# UNION the dimension tables with same schema
union_df = pd.concat([s0, s2, s6, s7], ignore_index=True)

# INNER JOIN with aspect tables on ROW_WID
df = union_df.merge(s1, on="ROW_WID", how="inner")
df = df.merge(s3, on="ROW_WID", how="inner")
df = df.merge(s4, on="ROW_WID", how="inner")
df = df.merge(s5, on="ROW_WID", how="inner")
df = df.merge(s8, on="ROW_WID", how="inner")
df = df.merge(s9, on="ROW_WID", how="inner")

# Define aggregation functions
agg_dict = {
    # Numeric float columns from dimension tables: mean
    'ARPU': 'mean',
    'MONTHS_AGE': 'mean',
    'HOME_PASSED': 'mean',
    # String columns: take first (non-null)
    'SES': 'first',
    'CUST_SINCE_DT': 'first',
    'CANCEL_DT': 'first',
    'CITY': 'first',
    'POP': 'first',
    # Integer count columns: sum
    'COLLECTION_EVENTS_NUM': 'sum',
    'INBOUND_CALLS_NUM': 'sum',
    'KEYWORDS_NUM': 'sum',
    'VISITS_NUM': 'sum',
    'TECHSUPPORT_NUM': 'sum',
    'INTERACTIONS_NUM': 'sum',
    # For ACCNT_LOC and CANCELED, take first (should be unique per ROW_WID)
    'ACCNT_LOC': 'first',
    'CANCELED': 'first',
}

# Group by CANCELED and ROW_WID (leftmost unique keys)
group_cols = ['CANCELED', 'ROW_WID']

# Because CANCELED is also aggregated by first, but is in group by, we can remove it from agg_dict
# Actually, since it's in group by, remove from agg_dict
agg_dict.pop('CANCELED')

# Perform groupby and aggregation
final_df = df.groupby(group_cols, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
        'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
        'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

final_df = final_df[cols]

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts.csv", index=False)