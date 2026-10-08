import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_3.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_9.csv", index_col=0)

union_df = pd.concat([df0, df2, df3, df9], ignore_index=True)

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_1.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_8.csv", index_col=0)

join1 = pd.merge(union_df, df1, on="ROW_WID", how="left")
join2 = pd.merge(join1, df4, on="ROW_WID", how="left")
join3 = pd.merge(join2, df5, on="ROW_WID", how="left")
join4 = pd.merge(join3, df6, on="ROW_WID", how="left")
join5 = pd.merge(join4, df7, on="ROW_WID", how="left")
final_df = pd.merge(join5, df8, on="ROW_WID", how="left")

final_df = final_df[['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']]

final_df['CANCELED'] = final_df['CANCELED'].astype('Int64')
final_df['ROW_WID'] = final_df['ROW_WID'].astype('Int64')
final_df['ACCNT_LOC'] = final_df['ACCNT_LOC'].astype('Int64')
final_df['ARPU'] = final_df['ARPU'].astype(float)
final_df['SES'] = final_df['SES'].astype(str)
final_df['HOME_PASSED'] = final_df['HOME_PASSED'].astype('Int64')
final_df['CUST_SINCE_DT'] = final_df['CUST_SINCE_DT'].astype(str)
final_df['MONTHS_AGE'] = final_df['MONTHS_AGE'].astype(float)
final_df['CANCEL_DT'] = final_df['CANCEL_DT'].astype(str)
final_df['CITY'] = final_df['CITY'].astype(str)
final_df['POP'] = final_df['POP'].astype(str)
final_df['COLLECTION_EVENTS_NUM'] = final_df['COLLECTION_EVENTS_NUM'].astype('Int64')
final_df['INBOUND_CALLS_NUM'] = final_df['INBOUND_CALLS_NUM'].astype('Int64')
final_df['KEYWORDS_NUM'] = final_df['KEYWORDS_NUM'].astype('Int64')
final_df['VISITS_NUM'] = final_df['VISITS_NUM'].astype('Int64')
final_df['TECHSUPPORT_NUM'] = final_df['TECHSUPPORT_NUM'].astype('Int64')
final_df['INTERACTIONS_NUM'] = final_df['INTERACTIONS_NUM'].astype('Int64')

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_27/target_multisource_mcts.csv", index=False)