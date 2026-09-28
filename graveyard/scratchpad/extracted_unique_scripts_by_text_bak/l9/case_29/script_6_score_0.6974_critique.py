import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_9.csv", index_col=0)

# UNION the four large tables with the same schema
union_df = pd.concat([s2, s5, s6, s9], ignore_index=True)

# JOIN union_df with s0 on ROW_WID
result = pd.merge(union_df, s0[['ROW_WID', 'COLLECTION_EVENTS_NUM']], on='ROW_WID', how='inner')

# JOIN with other source tables on ROW_WID
result = pd.merge(result, s1[['ROW_WID']], on='ROW_WID', how='inner')
result = pd.merge(result, s3[['ROW_WID']], on='ROW_WID', how='inner')
result = pd.merge(result, s4[['ROW_WID']], on='ROW_WID', how='inner')
result = pd.merge(result, s7[['ROW_WID']], on='ROW_WID', how='inner')
result = pd.merge(result, s8[['ROW_WID']], on='ROW_WID', how='inner')

# Select only COLLECTION_EVENTS_NUM column as target schema
final_result = result[['COLLECTION_EVENTS_NUM']].copy()
final_result['COLLECTION_EVENTS_NUM'] = final_result['COLLECTION_EVENTS_NUM'].astype(int)

final_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)