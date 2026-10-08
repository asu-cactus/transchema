import pandas as pd

# Load source tables
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

# Union tables with same schema (dimension tables): s3, s4, s7, s8
union_3_4_7_8 = pd.concat([s3, s4, s7, s8], ignore_index=True)

# Join all numeric tables on ROW_WID with the unioned dimension table
joined = union_3_4_7_8.merge(s0, on='ROW_WID', how='inner') \
                     .merge(s1, on='ROW_WID', how='inner') \
                     .merge(s2, on='ROW_WID', how='inner') \
                     .merge(s5, on='ROW_WID', how='inner') \
                     .merge(s6, on='ROW_WID', how='inner') \
                     .merge(s9, on='ROW_WID', how='inner')

# Select only the target column INBOUND_CALLS_NUM from s1
target = joined[['INBOUND_CALLS_NUM']]

# Ensure integer type as target schema requires integer
target['INBOUND_CALLS_NUM'] = target['INBOUND_CALLS_NUM'].astype('Int64')

# Save to target CSV
target.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)