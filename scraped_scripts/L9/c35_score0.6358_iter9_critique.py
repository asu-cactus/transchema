import pandas as pd

# Read all source CSVs with index_col=0
src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv', index_col=0)
src2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv', index_col=0)
src3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv', index_col=0)
src4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv', index_col=0)
src5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv', index_col=0)
src6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv', index_col=0)
src7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv', index_col=0)
src8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv', index_col=0)
src9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv', index_col=0)

# Step 1: UNION the 4 dimension tables with same schema
dim_union = pd.concat([src0, src1, src8, src9], ignore_index=True)

# Step 2: JOIN the unioned dimension table with all aspect tables on ROW_WID
# Start with dim_union
df = dim_union

# Join with Source9_35_2 (INBOUND_CALLS_NUM)
df = df.merge(src2, on='ROW_WID', how='left')

# Join with Source9_35_3 (KEYWORDS_NUM)
df = df.merge(src3, on='ROW_WID', how='left')

# Join with Source9_35_4 (TECHSUPPORT_NUM)
df = df.merge(src4, on='ROW_WID', how='left')

# Join with Source9_35_5 (INTERACTIONS_NUM)
df = df.merge(src5, on='ROW_WID', how='left')

# Join with Source9_35_6 (COLLECTION_EVENTS_NUM)
df = df.merge(src6, on='ROW_WID', how='left')

# Join with Source9_35_7 (VISITS_NUM)
df = df.merge(src7, on='ROW_WID', how='left')

# Step 3: GROUP BY ROW_WID, aggregate TECHSUPPORT_NUM by sum
# TECHSUPPORT_NUM may have NaNs, treat them as 0 for sum aggregation
df['TECHSUPPORT_NUM'] = df['TECHSUPPORT_NUM'].fillna(0)

agg_df = df.groupby('ROW_WID', as_index=False).agg({'TECHSUPPORT_NUM': 'sum'})

# Step 4: Project only TECHSUPPORT_NUM as target schema
result = agg_df[['TECHSUPPORT_NUM']]

# Write output CSV
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv', index=False)