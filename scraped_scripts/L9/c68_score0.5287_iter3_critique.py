import pandas as pd

# Read dimension tables with same schema
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_2.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_4.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_9.csv", index_col=0)

# Read aspect tables
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_1.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_3.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_8.csv", index_col=0)

# UNION dimension tables
union_dim = pd.concat([df0, df2, df4, df9], ignore_index=True)

# GROUP BY ROW_WID to remove duplicates, aggregate other columns
# For string columns and categorical columns, take first non-null value
# For numeric columns, take mean or first as appropriate

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
    'POP': 'first'
}

grouped_dim = union_dim.groupby('ROW_WID', as_index=False).agg(agg_dict)

# Join with aspect tables on ROW_WID using left joins
df = grouped_dim.merge(df1, on='ROW_WID', how='left') \
                .merge(df3, on='ROW_WID', how='left') \
                .merge(df5, on='ROW_WID', how='left') \
                .merge(df6, on='ROW_WID', how='left') \
                .merge(df7, on='ROW_WID', how='left') \
                .merge(df8, on='ROW_WID', how='left')

# Select columns in target schema order
result = df[[
    'CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
    'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
    'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM'
]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_68/target_multisource_mcts.csv", index=False)