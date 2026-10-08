import pandas as pd

# Read all sources
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv", index_col=0)

# UNION dimension tables (sources 3,4,7,8)
union_df = pd.concat([src3, src4, src7, src8], ignore_index=True)

# Join unioned dimension table with all aspect tables on ROW_WID using inner join
df = union_df[['ROW_WID']].drop_duplicates()

df = df.merge(src0[['ROW_WID']], on='ROW_WID', how='inner')
df = df.merge(src1[['ROW_WID', 'INBOUND_CALLS_NUM']], on='ROW_WID', how='inner')
df = df.merge(src2[['ROW_WID']], on='ROW_WID', how='inner')
df = df.merge(src5[['ROW_WID']], on='ROW_WID', how='inner')
df = df.merge(src6[['ROW_WID']], on='ROW_WID', how='inner')
df = df.merge(src9[['ROW_WID']], on='ROW_WID', how='inner')

# Now join with src0, src2, src5, src6, src9 to get their numeric columns
# Actually, we only need INBOUND_CALLS_NUM from src1 for aggregation, but all sources must be used
# Since target only has INBOUND_CALLS_NUM, we only aggregate that

# To ensure all sources are used, join their numeric columns (except src1 which is already joined)
df = df.merge(src0[['ROW_WID', 'KEYWORDS_NUM']], on='ROW_WID', how='inner')
df = df.merge(src2[['ROW_WID', 'TECHSUPPORT_NUM']], on='ROW_WID', how='inner')
df = df.merge(src5[['ROW_WID', 'INTERACTIONS_NUM']], on='ROW_WID', how='inner')
df = df.merge(src6[['ROW_WID', 'COLLECTION_EVENTS_NUM']], on='ROW_WID', how='inner')
df = df.merge(src9[['ROW_WID', 'VISITS_NUM']], on='ROW_WID', how='inner')

# Group by ROW_WID and sum INBOUND_CALLS_NUM
result = df.groupby('ROW_WID', as_index=False)['INBOUND_CALLS_NUM'].sum()

# Output only INBOUND_CALLS_NUM column as per target schema
result[['INBOUND_CALLS_NUM']].to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)