import pandas as pd

# Read dimension tables with same schema
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_2.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_4.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_9.csv", index_col=0)

# Union dimension tables
union_df = pd.concat([df0, df2, df4, df9], ignore_index=True)

# Read aspect tables
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_1.csv", index_col=0)  # TECHSUPPORT_NUM
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_3.csv", index_col=0)  # VISITS_NUM
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_5.csv", index_col=0)  # KEYWORDS_NUM
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_6.csv", index_col=0)  # INBOUND_CALLS_NUM
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_7.csv", index_col=0)  # INTERACTIONS_NUM
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_8.csv", index_col=0)  # COLLECTION_EVENTS_NUM

# Join all aspect tables on ROW_WID with left join to keep all dimension rows
merged = union_df.merge(df1, on="ROW_WID", how="left")
merged = merged.merge(df3, on="ROW_WID", how="left")
merged = merged.merge(df5, on="ROW_WID", how="left")
merged = merged.merge(df6, on="ROW_WID", how="left")
merged = merged.merge(df7, on="ROW_WID", how="left")
merged = merged.merge(df8, on="ROW_WID", how="left")

# Group by ROW_WID to remove duplicates and aggregate
agg_dict = {
    'CANCELED': 'first',
    'ACCNT_LOC': 'first',
    'ARPU': 'mean',
    'SES': 'first',
    'HOME_PASSED': 'first',
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

# Some count columns may have NaN after join, fill with 0 before sum aggregation
count_cols = ['COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']
merged[count_cols] = merged[count_cols].fillna(0)

result = merged.groupby('ROW_WID', as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
        'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
        'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM',
        'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

result = result[cols]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_68/target_multisource_mcts.csv", index=False)