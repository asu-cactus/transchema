import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_4.csv", index_col=0)
union_result = pd.concat([s0, s1, s3, s4], ignore_index=True)

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_2.csv", index_col=0)
join_result_1 = pd.merge(union_result, s2, on="ROW_WID", how="left")

s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_5.csv", index_col=0)
join_result_2 = pd.merge(join_result_1, s5, on="ROW_WID", how="left")

s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_6.csv", index_col=0)
join_result_3 = pd.merge(join_result_2, s6, on="ROW_WID", how="left")

s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_7.csv", index_col=0)
join_result_4 = pd.merge(join_result_3, s7, on="ROW_WID", how="left")

s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_8.csv", index_col=0)
join_result_5 = pd.merge(join_result_4, s8, on="ROW_WID", how="left")

s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_9.csv", index_col=0)
final_df = pd.merge(join_result_5, s9, on="ROW_WID", how="left")

cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']
final_df = final_df[cols]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_69/target_multisource_mcts.csv", index=False)