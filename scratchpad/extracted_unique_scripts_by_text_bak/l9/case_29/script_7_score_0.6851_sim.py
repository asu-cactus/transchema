import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_7.csv", index_col=0)

joined = pd.merge(s0, s7, on="ROW_WID", how="inner")

result = joined.groupby("COLLECTION_EVENTS_NUM", as_index=False).size().rename(columns={"size": "COUNT"})

# The target schema only requires COLLECTION_EVENTS_NUM, so we keep only that column.
# The target examples show only COLLECTION_EVENTS_NUM, so we output unique COLLECTION_EVENTS_NUM values.
# The GROUP_BY operation implies grouping by COLLECTION_EVENTS_NUM, but no aggregation is specified.
# Since target examples show only COLLECTION_EVENTS_NUM, we output unique values.

# So final output is unique COLLECTION_EVENTS_NUM values from s0 (joined with s7 as per plan).
# The join ensures only ROW_WID present in both sources are considered.

final = joined[["COLLECTION_EVENTS_NUM"]].drop_duplicates().reset_index(drop=True)

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)