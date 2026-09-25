import pandas as pd

# Load all source files
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)  # COLLECTION_EVENTS_NUM
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_1.csv", index_col=0)  # VISITS_NUM
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_2.csv", index_col=0)  # dimension
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_3.csv", index_col=0)  # INBOUND_CALLS_NUM
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_4.csv", index_col=0)  # KEYWORDS_NUM
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_5.csv", index_col=0)  # dimension
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_6.csv", index_col=0)  # dimension
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_7.csv", index_col=0)  # INTERACTIONS_NUM
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_8.csv", index_col=0)  # TECHSUPPORT_NUM
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_9.csv", index_col=0)  # dimension

# UNION dimension tables s2, s5, s6, s9
union_dim = pd.concat([s2, s5, s6, s9], ignore_index=True)

# JOIN s0 (COLLECTION_EVENTS_NUM) with union_dim on ROW_WID
joined = pd.merge(s0[['ROW_WID', 'COLLECTION_EVENTS_NUM']], union_dim[['ROW_WID']], on='ROW_WID', how='inner')

# JOIN with other aspect tables on ROW_WID
joined = pd.merge(joined, s1[['ROW_WID']], on='ROW_WID', how='inner')
joined = pd.merge(joined, s3[['ROW_WID']], on='ROW_WID', how='inner')
joined = pd.merge(joined, s4[['ROW_WID']], on='ROW_WID', how='inner')
joined = pd.merge(joined, s7[['ROW_WID']], on='ROW_WID', how='inner')
joined = pd.merge(joined, s8[['ROW_WID']], on='ROW_WID', how='inner')

# The target only requires COLLECTION_EVENTS_NUM column
joined[['COLLECTION_EVENTS_NUM']].to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)