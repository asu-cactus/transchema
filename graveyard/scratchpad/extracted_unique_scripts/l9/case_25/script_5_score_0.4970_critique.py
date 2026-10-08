import pandas as pd

# Read all source tables
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_9.csv", index_col=0)

# UNION the four tables with the same schema
unioned = pd.concat([source0, source1, source4, source5], ignore_index=True)

# JOIN unioned with all other tables on ROW_WID
df = unioned.merge(source2, on='ROW_WID', how='left') \
             .merge(source3, on='ROW_WID', how='left') \
             .merge(source6, on='ROW_WID', how='left') \
             .merge(source7, on='ROW_WID', how='left') \
             .merge(source8, on='ROW_WID', how='left') \
             .merge(source9, on='ROW_WID', how='left')

# GROUP BY ROW_WID, aggregate CANCEL_DT by first non-null value
# pandas 'first' aggregation keeps the first non-null value in the group
agg_df = df.groupby('ROW_WID', as_index=False).agg({'CANCEL_DT': 'first'})

# Project CANCEL_DT only
result = agg_df[['CANCEL_DT']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)