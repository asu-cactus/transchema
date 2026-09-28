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

# Union tables with same schema (D/E/H/I): s3, s4, s7, s8
union_3_4_7_8 = pd.concat([s3, s4, s7, s8], ignore_index=True)

# Unpivot numeric columns from s0, s1, s2, s5, s6, s9
# Each has schema: ['ROW_WID', <metric>]
# We rename the metric column to a common name 'metric' and keep 'ROW_WID' and 'value'
def unpivot(df):
    id_col = 'ROW_WID'
    val_col = [c for c in df.columns if c != id_col][0]
    df_unpivot = df.rename(columns={val_col: 'INBOUND_CALLS_NUM'})[['ROW_WID', 'INBOUND_CALLS_NUM']]
    return df_unpivot

u0 = s0.rename(columns={'KEYWORDS_NUM':'INBOUND_CALLS_NUM'})[['ROW_WID','INBOUND_CALLS_NUM']]
u1 = s1[['ROW_WID','INBOUND_CALLS_NUM']]
u2 = s2.rename(columns={'TECHSUPPORT_NUM':'INBOUND_CALLS_NUM'})[['ROW_WID','INBOUND_CALLS_NUM']]
u5 = s5.rename(columns={'INTERACTIONS_NUM':'INBOUND_CALLS_NUM'})[['ROW_WID','INBOUND_CALLS_NUM']]
u6 = s6.rename(columns={'COLLECTION_EVENTS_NUM':'INBOUND_CALLS_NUM'})[['ROW_WID','INBOUND_CALLS_NUM']]
u9 = s9.rename(columns={'VISITS_NUM':'INBOUND_CALLS_NUM'})[['ROW_WID','INBOUND_CALLS_NUM']]

unpivot_result = pd.concat([u0,u1,u2,u5,u6,u9], ignore_index=True)

# Join unpivot_result with union_3_4_7_8 on ROW_WID
joined = pd.merge(unpivot_result, union_3_4_7_8[['ROW_WID']], on='ROW_WID', how='inner')

# Select only the target column INBOUND_CALLS_NUM
target = joined[['INBOUND_CALLS_NUM']]

# Ensure integer type as target schema requires integer
target['INBOUND_CALLS_NUM'] = target['INBOUND_CALLS_NUM'].astype('Int64')

# Save to target CSV
target.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)