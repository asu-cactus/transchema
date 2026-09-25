import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv", index_col=0)

union_3_4_7_8 = pd.concat([s3, s4, s7, s8], ignore_index=True)

merged = union_3_4_7_8.merge(s0[['ROW_WID', 'KEYWORDS_NUM']], on='ROW_WID', how='left') \
    .merge(s1[['ROW_WID', 'INBOUND_CALLS_NUM']], on='ROW_WID', how='left') \
    .merge(s2[['ROW_WID', 'TECHSUPPORT_NUM']], on='ROW_WID', how='left') \
    .merge(s5[['ROW_WID', 'INTERACTIONS_NUM']], on='ROW_WID', how='left') \
    .merge(s6[['ROW_WID', 'COLLECTION_EVENTS_NUM']], on='ROW_WID', how='left') \
    .merge(s9[['ROW_WID', 'VISITS_NUM']], on='ROW_WID', how='left')

result = merged[['INBOUND_CALLS_NUM']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)