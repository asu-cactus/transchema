import pandas as pd

source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)

joined = pd.merge(source1, source5, on="ROW_WID")

result = joined.groupby("INBOUND_CALLS_NUM", as_index=False).size().rename(columns={"size": "count"})

# The target schema only requires INBOUND_CALLS_NUM column, so we keep unique INBOUND_CALLS_NUM values.
# The target examples show counts of occurrences, but the target schema only has INBOUND_CALLS_NUM column.
# So we just output the distinct INBOUND_CALLS_NUM values as rows.

# Since the target examples show counts of INBOUND_CALLS_NUM values, but the schema only has that column,
# we output the distinct INBOUND_CALLS_NUM values (one row per value).

# So final output is unique INBOUND_CALLS_NUM values, no aggregation count column.

final = pd.DataFrame(result["INBOUND_CALLS_NUM"])

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)