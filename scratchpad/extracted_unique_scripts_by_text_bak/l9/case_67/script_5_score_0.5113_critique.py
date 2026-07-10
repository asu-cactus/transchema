import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_9.csv", index_col=0)

# UNION the four dimension tables with same schema
union_dim = pd.concat([s2, s3, s4, s9], ignore_index=True)

# Group by the leftmost unique key columns to remove duplicates and aggregate
# Group by columns: 'CANCELED', 'ROW_WID', 'ACCNT_LOC'
# Aggregations:
# - ARPU (float): mean
# - SES (string): max (to pick one, max is arbitrary but consistent)
# - HOME_PASSED (int): sum (count-like)
# - CUST_SINCE_DT (string): max (pick latest date string lex order)
# - MONTHS_AGE (float): mean
# - CANCEL_DT (string): max (pick latest date string lex order)
# - CITY (string): max
# - POP (string): max

agg_dict = {
    'ARPU': 'mean',
    'SES': 'max',
    'HOME_PASSED': 'sum',
    'CUST_SINCE_DT': 'max',
    'MONTHS_AGE': 'mean',
    'CANCEL_DT': 'max',
    'CITY': 'max',
    'POP': 'max'
}

union_grouped = union_dim.groupby(['CANCELED', 'ROW_WID', 'ACCNT_LOC'], as_index=False).agg(agg_dict)

# Join with all aspect tables on ROW_WID using left joins
df = union_grouped.merge(s0, on='ROW_WID', how='left') \
                  .merge(s1, on='ROW_WID', how='left') \
                  .merge(s5, on='ROW_WID', how='left') \
                  .merge(s6, on='ROW_WID', how='left') \
                  .merge(s7, on='ROW_WID', how='left') \
                  .merge(s8, on='ROW_WID', how='left')

# Select columns in target schema order
result = df[[
    'CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
    'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
    'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM'
]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_67/target_multisource_mcts.csv", index=False)