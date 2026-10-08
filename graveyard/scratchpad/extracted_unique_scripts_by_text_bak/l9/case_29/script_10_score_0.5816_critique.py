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

# UNION all dimension tables with same schema
union_259 = pd.concat([s2, s5, s6, s9], ignore_index=True)

# JOIN unioned dimension table with all aspect tables on ROW_WID
join_1 = pd.merge(union_259, s0, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, s1, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, s3, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, s4, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, s7, on="ROW_WID", how="inner")
join_6 = pd.merge(join_5, s8, on="ROW_WID", how="inner")

# Select distinct COLLECTION_EVENTS_NUM values as target schema requires
result = join_6[["COLLECTION_EVENTS_NUM"]].drop_duplicates().reset_index(drop=True)
result["COLLECTION_EVENTS_NUM"] = result["COLLECTION_EVENTS_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)