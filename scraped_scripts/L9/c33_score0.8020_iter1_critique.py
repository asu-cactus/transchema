import pandas as pd

# Load source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)

# UNION step: union s4,s5,s7,s9 (dimension tables with same schema)
unioned_dim = pd.concat([s4, s5, s7, s9], ignore_index=True)

# JOIN all *_NUM tables on ROW_WID
join_01 = pd.merge(s0, s1, on='ROW_WID', how='inner')
join_012 = pd.merge(join_01, s2, on='ROW_WID', how='inner')
join_0123 = pd.merge(join_012, s3, on='ROW_WID', how='inner')
join_01236 = pd.merge(join_0123, s6, on='ROW_WID', how='inner')
join_all_num = pd.merge(join_01236, s8, on='ROW_WID', how='inner')

# JOIN unioned dimension with joined numeric tables on ROW_WID
joined = pd.merge(unioned_dim, join_all_num, on='ROW_WID', how='inner')

# Create INTERACTIONS_NUM as sum of all *_NUM columns from numeric tables
# Columns from numeric tables: VISITS_NUM, COLLECTION_EVENTS_NUM, TECHSUPPORT_NUM, KEYWORDS_NUM, INBOUND_CALLS_NUM, INTERACTIONS_NUM
joined['INTERACTIONS_NUM'] = (
    joined['VISITS_NUM'] +
    joined['COLLECTION_EVENTS_NUM'] +
    joined['TECHSUPPORT_NUM'] +
    joined['KEYWORDS_NUM'] +
    joined['INBOUND_CALLS_NUM'] +
    joined['INTERACTIONS_NUM']
)

# GROUP BY no columns (aggregate sum of INTERACTIONS_NUM) to remove duplicates
# Since target schema has only INTERACTIONS_NUM, and no key columns, group by nothing
result = pd.DataFrame({'INTERACTIONS_NUM': [joined['INTERACTIONS_NUM'].sum()]})

# But target examples have multiple rows, so grouping by nothing is not correct.
# Instead, group by ROW_WID and sum INTERACTIONS_NUM per ROW_WID, then project INTERACTIONS_NUM only
result = joined.groupby('ROW_WID', as_index=False)['INTERACTIONS_NUM'].sum()

# Project only INTERACTIONS_NUM column as target schema
result = result[['INTERACTIONS_NUM']]

# Save result
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)