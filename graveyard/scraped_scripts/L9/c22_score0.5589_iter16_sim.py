import pandas as pd

# Load source tables
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv", index_col=0)

# Unpivot source tables with one numeric column besides ROW_WID to a common schema: ROW_WID, INBOUND_CALLS_NUM
def unpivot(df, value_col):
    return df.rename(columns={value_col: 'INBOUND_CALLS_NUM'})[['ROW_WID', 'INBOUND_CALLS_NUM']]

up0 = unpivot(src0, 'KEYWORDS_NUM')
up1 = unpivot(src1, 'INBOUND_CALLS_NUM')
up2 = unpivot(src2, 'TECHSUPPORT_NUM')
up5 = unpivot(src5, 'INTERACTIONS_NUM')
up6 = unpivot(src6, 'COLLECTION_EVENTS_NUM')
up9 = unpivot(src9, 'VISITS_NUM')

# Union only the tables that already have the target column name INBOUND_CALLS_NUM (src1, src5, src6, src9)
union_df = pd.concat([up1, up5, up6, up9], ignore_index=True)

# Combine all unpivoted tables (including those renamed) into one dataframe
all_unpivoted = pd.concat([up0, up2, union_df], ignore_index=True)

# Select only the target column INBOUND_CALLS_NUM as integer
result = all_unpivoted[['INBOUND_CALLS_NUM']].copy()
result['INBOUND_CALLS_NUM'] = result['INBOUND_CALLS_NUM'].astype('Int64')

# Save to target CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)