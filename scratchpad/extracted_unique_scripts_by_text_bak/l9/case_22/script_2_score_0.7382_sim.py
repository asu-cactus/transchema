import pandas as pd

# Load source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv", index_col=0)

# UNPIVOT operation on sources with one numeric column besides ROW_WID
def unpivot(df, id_col):
    value_cols = [c for c in df.columns if c != id_col]
    return df.melt(id_vars=[id_col], value_vars=value_cols, var_name="metric", value_name="value")

u0 = unpivot(s0, "ROW_WID")
u1 = unpivot(s1, "ROW_WID")
u2 = unpivot(s2, "ROW_WID")
u5 = unpivot(s5, "ROW_WID")
u6 = unpivot(s6, "ROW_WID")
u9 = unpivot(s9, "ROW_WID")

unpivoted = pd.concat([u0, u1, u2, u5, u6, u9], ignore_index=True)

# UNION operation on sources with same schema (the 4 sources with many columns)
unioned = pd.concat([s3, s4, s7, s8], ignore_index=True)

# JOIN unpivoted and unioned on ROW_WID
joined = pd.merge(unpivoted, unioned, on="ROW_WID", how="inner")

# Filter rows where metric == 'INBOUND_CALLS_NUM' and select that value as target column
target_df = joined[joined["metric"] == "INBOUND_CALLS_NUM"][["value"]].copy()
target_df.rename(columns={"value": "INBOUND_CALLS_NUM"}, inplace=True)
target_df["INBOUND_CALLS_NUM"] = target_df["INBOUND_CALLS_NUM"].astype("Int64")

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)