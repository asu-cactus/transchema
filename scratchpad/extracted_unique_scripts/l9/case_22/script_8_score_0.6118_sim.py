import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, on="ROW_WID", how="inner")

result = merged.groupby("INBOUND_CALLS_NUM", as_index=False).size().rename(columns={"size": "count"})

# The target schema only requires INBOUND_CALLS_NUM column, so we keep it as is.
# The target examples show just the INBOUND_CALLS_NUM column, so we output that column only.
# The GROUP_BY operation implies grouping by INBOUND_CALLS_NUM, but no aggregation is specified for other columns.
# Since the target schema is only INBOUND_CALLS_NUM, we output unique INBOUND_CALLS_NUM values.
# The count column is not part of the target schema, so we drop it.

final = result[["INBOUND_CALLS_NUM"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)