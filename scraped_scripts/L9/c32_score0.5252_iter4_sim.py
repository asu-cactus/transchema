import pandas as pd

source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_9.csv", index_col=0)

joined = pd.merge(source1, source9, on="ROW_WID")

result = joined.groupby("VISITS_NUM", as_index=False).size().rename(columns={"size": "COUNT"})

# The target schema only requires VISITS_NUM column, so we keep only that column.
# The target examples show only VISITS_NUM, so we drop the count column.
# The GROUP_BY operation implies grouping by VISITS_NUM, but no aggregation is specified for VISITS_NUM itself.
# Since the target table only has VISITS_NUM column, we just keep unique VISITS_NUM values.

result = result[["VISITS_NUM"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)