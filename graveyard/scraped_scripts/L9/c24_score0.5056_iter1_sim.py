import pandas as pd

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

union_df = pd.concat([s0, s2, s6, s7], ignore_index=True)

join_1 = pd.merge(union_df, s1, on="ROW_WID", how="left")
join_2 = pd.merge(join_1, s3, on="ROW_WID", how="left")
join_3 = pd.merge(join_2, s4, on="ROW_WID", how="left")
join_4 = pd.merge(join_3, s5, on="ROW_WID", how="left")
join_5 = pd.merge(join_4, s8, on="ROW_WID", how="left")
join_6 = pd.merge(join_5, s9, on="ROW_WID", how="left")

final_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
              'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

result = join_6[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts.csv", index=False)