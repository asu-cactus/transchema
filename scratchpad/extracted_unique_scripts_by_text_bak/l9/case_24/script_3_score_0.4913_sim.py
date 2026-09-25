import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_0.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_2.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_7.csv", index_col=0)

union_result = pd.concat([s0, s2, s6, s7], ignore_index=True)

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_1.csv", index_col=0)
join_result_1 = pd.merge(union_result, s1, on="ROW_WID", how="left")

s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_3.csv", index_col=0)
join_result_2 = pd.merge(join_result_1, s3, on="ROW_WID", how="left")

s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_4.csv", index_col=0)
join_result_3 = pd.merge(join_result_2, s4, on="ROW_WID", how="left")

s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_5.csv", index_col=0)
join_result_4 = pd.merge(join_result_3, s5, on="ROW_WID", how="left")

s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_8.csv", index_col=0)
join_result_5 = pd.merge(join_result_4, s8, on="ROW_WID", how="left")

s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_9.csv", index_col=0)
final_df = pd.merge(join_result_5, s9, on="ROW_WID", how="left")

cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']
final_df = final_df[cols]

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

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts.csv", index=False)