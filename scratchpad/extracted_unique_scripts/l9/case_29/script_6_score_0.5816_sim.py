import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_9.csv", index_col=0)

union_259 = pd.concat([s2, s5, s6, s9], ignore_index=True)

join_1 = pd.merge(union_259, s0, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, s1, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, s3, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, s4, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, s7, on="ROW_WID", how="inner")
join_6 = pd.merge(join_5, s8, on="ROW_WID", how="inner")

result = join_6.groupby("COLLECTION_EVENTS_NUM", as_index=False).size()
result = result.rename(columns={"size": "COLLECTION_EVENTS_NUM"})
# The above line renames the count column to COLLECTION_EVENTS_NUM, but target expects COLLECTION_EVENTS_NUM as integer values, not counts.
# The target schema is just COLLECTION_EVENTS_NUM integer values, and target examples show values of COLLECTION_EVENTS_NUM, not counts.
# So the GROUP_BY : [COLLECTION_EVENTS_NUM] means just group by COLLECTION_EVENTS_NUM and output unique COLLECTION_EVENTS_NUM values.
# So the output should be unique COLLECTION_EVENTS_NUM values from the joined data.

# So instead of counting, just get unique COLLECTION_EVENTS_NUM values from the joined data.

result = join_6[["COLLECTION_EVENTS_NUM"]].drop_duplicates().reset_index(drop=True)
result["COLLECTION_EVENTS_NUM"] = result["COLLECTION_EVENTS_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)