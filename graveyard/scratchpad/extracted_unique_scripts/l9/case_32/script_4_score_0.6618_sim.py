import pandas as pd

# Load source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_9.csv", index_col=0)

# Unpivot sources 0,1,2,3,4,9 to long format with columns ROW_WID, metric_name, metric_value
def unpivot(df, value_col):
    return df.rename(columns={value_col: "value"}).assign(metric=value_col)[["ROW_WID", "metric", "value"]]

u0 = unpivot(s0, "INBOUND_CALLS_NUM")
u1 = unpivot(s1, "VISITS_NUM")
u2 = unpivot(s2, "KEYWORDS_NUM")
u3 = unpivot(s3, "INTERACTIONS_NUM")
u4 = unpivot(s4, "COLLECTION_EVENTS_NUM")
u9 = unpivot(s9, "TECHSUPPORT_NUM")

unpivoted = pd.concat([u0, u1, u2, u3, u4, u9], ignore_index=True)

# Pivot back to wide format to get all *_NUM columns per ROW_WID
wide = unpivoted.pivot_table(index="ROW_WID", columns="metric", values="value", aggfunc='first').reset_index()

# Union sources 5,6,7,8 (same schema)
union_5_6_7_8 = pd.concat([s5, s6, s7, s8], ignore_index=True)

# Join wide (metrics) with union_5_6_7_8 on ROW_WID
joined = pd.merge(wide, union_5_6_7_8, on="ROW_WID", how="inner")

# The target schema is ['VISITS_NUM'] only, so select that column
result = joined[["VISITS_NUM"]]

# Ensure VISITS_NUM is integer type (as target schema)
result["VISITS_NUM"] = result["VISITS_NUM"].astype("Int64")

# Save to target CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)