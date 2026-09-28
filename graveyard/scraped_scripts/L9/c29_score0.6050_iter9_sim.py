import pandas as pd

# Load source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_4.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_8.csv", index_col=0)

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_2.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_6.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_9.csv", index_col=0)

# UNPIVOT step: convert each source with one numeric column (other than ROW_WID) into a common schema with ROW_WID and COLLECTION_EVENTS_NUM
def unpivot_source(df):
    id_col = 'ROW_WID'
    val_col = [c for c in df.columns if c != id_col][0]
    return df.rename(columns={val_col: 'COLLECTION_EVENTS_NUM'})[[id_col, 'COLLECTION_EVENTS_NUM']]

unpivoted_dfs = [unpivot_source(df) for df in [s0, s1, s3, s4, s7, s8]]
unpivoted = pd.concat(unpivoted_dfs, ignore_index=True)

# UNION step: union all sources with the same schema (the large tables with many columns)
unioned = pd.concat([s2, s5, s6, s9], ignore_index=True)

# JOIN step: join unpivoted and unioned on ROW_WID
joined = pd.merge(unpivoted, unioned, on='ROW_WID', how='inner')

# PROJECT step: select only COLLECTION_EVENTS_NUM from unpivoted side (left)
result = joined[['COLLECTION_EVENTS_NUM']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)