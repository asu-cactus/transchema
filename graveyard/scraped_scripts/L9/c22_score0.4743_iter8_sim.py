import pandas as pd

# Load source tables
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv", index_col=0)

# Prepare each source by renaming the numeric columns to a common name and unpivoting
def unpivot_source(df, value_col):
    df2 = df[['ROW_WID', value_col]].copy()
    df2 = df2.rename(columns={value_col: 'INBOUND_CALLS_NUM'})
    return df2

u0 = unpivot_source(src0, 'KEYWORDS_NUM')
u1 = unpivot_source(src1, 'INBOUND_CALLS_NUM')
u2 = unpivot_source(src2, 'TECHSUPPORT_NUM')
u5 = unpivot_source(src5, 'INTERACTIONS_NUM')
u6 = unpivot_source(src6, 'COLLECTION_EVENTS_NUM')
u9 = unpivot_source(src9, 'VISITS_NUM')

# Concatenate all unpivoted data
concat_all = pd.concat([u0, u1, u2, u5, u6, u9], ignore_index=True)

# Group by INBOUND_CALLS_NUM and count occurrences
result = concat_all.groupby('INBOUND_CALLS_NUM', as_index=False).size()
result = result.rename(columns={'size': 'INBOUND_CALLS_NUM'})

# The target schema is ['INBOUND_CALLS_NUM': integer]
# The target examples show INBOUND_CALLS_NUM as integer values, so ensure dtype
result['INBOUND_CALLS_NUM'] = result['INBOUND_CALLS_NUM'].astype(int)

# Save to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)