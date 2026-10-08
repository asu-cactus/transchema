import pandas as pd

# Read source tables with index_col=0 as per hint 22
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)

# UNION all base tables with the same schema
base_union = pd.concat([source0, source1, source8, source9], ignore_index=True)

# Join with aspect tables on ROW_WID
joined = base_union.merge(source2, on="ROW_WID", how="inner") \
                   .merge(source3, on="ROW_WID", how="inner") \
                   .merge(source4, on="ROW_WID", how="inner") \
                   .merge(source5, on="ROW_WID", how="inner") \
                   .merge(source6, on="ROW_WID", how="inner") \
                   .merge(source7, on="ROW_WID", how="inner")

# Aggregate TECHSUPPORT_NUM by sum (no group by)
# Since target schema only has TECHSUPPORT_NUM, output that column only
# Sum TECHSUPPORT_NUM over all rows
techsupport_sum = joined["TECHSUPPORT_NUM"].sum()

# Create final DataFrame with one column TECHSUPPORT_NUM and rows equal to the count of unique ROW_WID
# But target has 4161 rows, so likely we need to group by ROW_WID and sum TECHSUPPORT_NUM per ROW_WID
# Let's group by ROW_WID and sum TECHSUPPORT_NUM, then output only TECHSUPPORT_NUM column

final_df = joined.groupby("ROW_WID", as_index=False)["TECHSUPPORT_NUM"].sum()

# Project only TECHSUPPORT_NUM column as per target schema
final_df = final_df[["TECHSUPPORT_NUM"]]

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)