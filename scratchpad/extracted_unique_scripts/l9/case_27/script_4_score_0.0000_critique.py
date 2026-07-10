import pandas as pd

# Read source tables with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_3.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_9.csv", index_col=0)

# Union the four large tables with the same schema
union_df = pd.concat([df0, df2, df3, df9], ignore_index=True)

# Read aspect tables
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_1.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_8.csv", index_col=0)

# Join all aspect tables on ROW_WID
join1 = pd.merge(union_df, df1, on="ROW_WID", how="left")
join2 = pd.merge(join1, df4, on="ROW_WID", how="left")
join3 = pd.merge(join2, df5, on="ROW_WID", how="left")
join4 = pd.merge(join3, df6, on="ROW_WID", how="left")
join5 = pd.merge(join4, df7, on="ROW_WID", how="left")
final_join = pd.merge(join5, df8, on="ROW_WID", how="left")

# Group by leftmost non-float columns that form unique key in target
group_by_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'CANCEL_DT', 'CITY', 'POP']

# Aggregations:
# ARPU and MONTHS_AGE: mean
# *_NUM columns: sum
agg_dict = {
    'ARPU': 'mean',
    'MONTHS_AGE': 'mean',
    'COLLECTION_EVENTS_NUM': 'sum',
    'INBOUND_CALLS_NUM': 'sum',
    'KEYWORDS_NUM': 'sum',
    'VISITS_NUM': 'sum',
    'TECHSUPPORT_NUM': 'sum',
    'INTERACTIONS_NUM': 'sum'
}

# Perform groupby and aggregation
final_df = final_join.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
final_df = final_df[['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
                     'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
                     'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']]

# Write to CSV without index
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_27/target_multisource_mcts.csv", index=False)