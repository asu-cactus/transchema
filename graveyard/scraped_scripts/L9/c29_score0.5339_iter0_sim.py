import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)

result = df0.groupby("COLLECTION_EVENTS_NUM", as_index=False).size().rename(columns={"size": "count"})

# The target schema only requires COLLECTION_EVENTS_NUM as integer, no aggregation count column needed.
# The target examples show just the distinct COLLECTION_EVENTS_NUM values, so we just need unique values.

result = df0[["COLLECTION_EVENTS_NUM"]].drop_duplicates().reset_index(drop=True)
result["COLLECTION_EVENTS_NUM"] = result["COLLECTION_EVENTS_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)