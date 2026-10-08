import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_0.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_4.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_9.csv", index_col=0)

union_df = pd.concat([s0, s2, s4, s9], ignore_index=True)

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_1.csv", index_col=0)
join_1 = pd.merge(union_df, s1, on="ROW_WID", how="left")

s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_3.csv", index_col=0)
join_2 = pd.merge(join_1, s3, on="ROW_WID", how="left")

s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_5.csv", index_col=0)
join_3 = pd.merge(join_2, s5, on="ROW_WID", how="left")

s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_6.csv", index_col=0)
join_4 = pd.merge(join_3, s6, on="ROW_WID", how="left")

s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_7.csv", index_col=0)
join_5 = pd.merge(join_4, s7, on="ROW_WID", how="left")

s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_8.csv", index_col=0)
final_df = pd.merge(join_5, s8, on="ROW_WID", how="left")

cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']
final_df = final_df[cols]

final_df['CANCELED'] = final_df['CANCELED'].astype('Int64')
final_df['ROW_WID'] = final_df['ROW_WID'].astype('Int64')
final_df['ACCNT_LOC'] = final_df['ACCNT_LOC'].astype('Int64')
final_df['ARPU'] = final_df['ARPU'].astype(float)
final_df['HOME_PASSED'] = final_df['HOME_PASSED'].astype('Int64')
final_df['MONTHS_AGE'] = final_df['MONTHS_AGE'].astype(float)
final_df['COLLECTION_EVENTS_NUM'] = final_df['COLLECTION_EVENTS_NUM'].astype('Int64')
final_df['INBOUND_CALLS_NUM'] = final_df['INBOUND_CALLS_NUM'].astype('Int64')
final_df['KEYWORDS_NUM'] = final_df['KEYWORDS_NUM'].astype('Int64')
final_df['VISITS_NUM'] = final_df['VISITS_NUM'].astype('Int64')
final_df['TECHSUPPORT_NUM'] = final_df['TECHSUPPORT_NUM'].astype('Int64')
final_df['INTERACTIONS_NUM'] = final_df['INTERACTIONS_NUM'].astype('Int64')

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_68/target_multisource_mcts.csv", index=False)