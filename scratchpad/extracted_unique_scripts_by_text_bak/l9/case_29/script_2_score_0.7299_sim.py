import pandas as pd

# Load all source files
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

# Unpivot sources with schema ['ROW_WID', <metric>]
def unpivot_source(df):
    id_col = 'ROW_WID'
    value_cols = [c for c in df.columns if c != id_col]
    unpivoted = df.melt(id_vars=id_col, value_vars=value_cols, var_name='metric_name', value_name='metric_value')
    return unpivoted

unpivoted_0 = unpivot_source(s0)
unpivoted_1 = unpivot_source(s1)
unpivoted_3 = unpivot_source(s3)
unpivoted_4 = unpivot_source(s4)
unpivoted_7 = unpivot_source(s7)
unpivoted_8 = unpivot_source(s8)

unpivoted_all = pd.concat([unpivoted_0, unpivoted_1, unpivoted_3, unpivoted_4, unpivoted_7, unpivoted_8], ignore_index=True)

# Filter only rows where metric_name == 'COLLECTION_EVENTS_NUM' because target only has COLLECTION_EVENTS_NUM
unpivoted_collection = unpivoted_all[unpivoted_all['metric_name'] == 'COLLECTION_EVENTS_NUM'][['ROW_WID', 'metric_value']]
unpivoted_collection = unpivoted_collection.rename(columns={'metric_value': 'COLLECTION_EVENTS_NUM'})

# Union sources with schema like s2, s5, s6, s9 (all have no COLLECTION_EVENTS_NUM column)
union_2_5_6_9 = pd.concat([s2, s5, s6, s9], ignore_index=True)

# Join unpivoted_collection with union_2_5_6_9 on ROW_WID
joined = pd.merge(unpivoted_collection, union_2_5_6_9[['ROW_WID']], on='ROW_WID', how='inner')

# The target only requires COLLECTION_EVENTS_NUM column, so group by ROW_WID and sum COLLECTION_EVENTS_NUM
result = joined.groupby('ROW_WID', as_index=False).agg({'COLLECTION_EVENTS_NUM': 'sum'})

# Save result
result[['COLLECTION_EVENTS_NUM']].to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)