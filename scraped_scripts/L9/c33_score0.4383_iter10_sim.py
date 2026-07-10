import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)

j0 = pd.merge(s8, s0, on="ROW_WID", how="inner")
j1 = pd.merge(j0, s1, on="ROW_WID", how="inner")
j2 = pd.merge(j1, s2, on="ROW_WID", how="inner")
j3 = pd.merge(j2, s3, on="ROW_WID", how="inner")
j4 = pd.merge(j3, s6, on="ROW_WID", how="inner")

agg = j4.groupby("INTERACTIONS_NUM").agg(
    INTERACTIONS_NUM_count = ("ROW_WID", "count"),
    VISITS_NUM_sum = ("VISITS_NUM", "sum"),
    COLLECTION_EVENTS_NUM_sum = ("COLLECTION_EVENTS_NUM", "sum"),
    TECHSUPPORT_NUM_sum = ("TECHSUPPORT_NUM", "sum"),
    KEYWORDS_NUM_sum = ("KEYWORDS_NUM", "sum"),
    INBOUND_CALLS_NUM_sum = ("INBOUND_CALLS_NUM", "sum"),
).reset_index()

result = agg[["INTERACTIONS_NUM_count"]].rename(columns={"INTERACTIONS_NUM_count": "INTERACTIONS_NUM"})
result["INTERACTIONS_NUM"] = result["INTERACTIONS_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)