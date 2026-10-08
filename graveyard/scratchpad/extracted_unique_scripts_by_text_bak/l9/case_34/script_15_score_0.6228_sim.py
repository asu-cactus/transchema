import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

j0 = pd.merge(s9, s0, on="ROW_WID", how="inner")
j1 = pd.merge(j0, s1, on="ROW_WID", how="inner")
j2 = pd.merge(j1, s3, on="ROW_WID", how="inner")
j3 = pd.merge(j2, s4, on="ROW_WID", how="inner")
j4 = pd.merge(j3, s7, on="ROW_WID", how="inner")

agg = j4.groupby("KEYWORDS_NUM").agg({
    "COLLECTION_EVENTS_NUM": "sum",
    "INTERACTIONS_NUM": "sum",
    "TECHSUPPORT_NUM": "sum",
    "VISITS_NUM": "sum",
    "INBOUND_CALLS_NUM": "sum"
}).reset_index()

agg["KEYWORDS_NUM"] = agg["KEYWORDS_NUM"].astype(int)

agg[["KEYWORDS_NUM"]].to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)