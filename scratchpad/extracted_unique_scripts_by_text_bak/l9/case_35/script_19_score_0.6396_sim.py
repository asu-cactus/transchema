import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)

union_0_1_8_9 = pd.concat([s0, s1, s8, s9], ignore_index=True)

join_0_1_8_9_2 = pd.merge(union_0_1_8_9, s2, on="ROW_WID", how="inner")
join_0_1_8_9_2_3 = pd.merge(join_0_1_8_9_2, s3, on="ROW_WID", how="inner")
join_0_1_8_9_2_3_4 = pd.merge(join_0_1_8_9_2_3, s4, on="ROW_WID", how="inner")
join_0_1_8_9_2_3_4_5 = pd.merge(join_0_1_8_9_2_3_4, s5, on="ROW_WID", how="inner")
join_0_1_8_9_2_3_4_5_6 = pd.merge(join_0_1_8_9_2_3_4_5, s6, on="ROW_WID", how="inner")
join_0_1_8_9_2_3_4_5_6_7 = pd.merge(join_0_1_8_9_2_3_4_5_6, s7, on="ROW_WID", how="inner")

agg = join_0_1_8_9_2_3_4_5_6_7.groupby("TECHSUPPORT_NUM", as_index=False).agg({
    "INBOUND_CALLS_NUM": "sum",
    "INTERACTIONS_NUM": "sum",
    "COLLECTION_EVENTS_NUM": "sum",
    "VISITS_NUM": "sum"
})

result = agg[["TECHSUPPORT_NUM"]].copy()
result["TECHSUPPORT_NUM"] = result["TECHSUPPORT_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)