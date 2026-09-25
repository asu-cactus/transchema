import pandas as pd

# Load source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

# Unpivot numeric columns from sources with single numeric columns (except s9 which already has KEYWORDS_NUM)
def unpivot_num(df, key_col):
    value_cols = [c for c in df.columns if c != key_col]
    return df.melt(id_vars=[key_col], value_vars=value_cols, var_name="metric", value_name="KEYWORDS_NUM")[[key_col, "KEYWORDS_NUM"]]

u0 = unpivot_num(s0, "ROW_WID")
u1 = unpivot_num(s1, "ROW_WID")
u3 = unpivot_num(s3, "ROW_WID")
u4 = unpivot_num(s4, "ROW_WID")
u7 = unpivot_num(s7, "ROW_WID")
u9 = s9[["ROW_WID", "KEYWORDS_NUM"]].copy()

unpivoted = pd.concat([u0, u1, u3, u4, u7, u9], ignore_index=True)

# Union the canceled-related sources (s2, s5, s6, s8) which share the same schema
canceled_union = pd.concat([s2, s5, s6, s8], ignore_index=True)

# Join unpivoted numeric data with canceled_union on ROW_WID
joined = pd.merge(unpivoted, canceled_union, on="ROW_WID", how="inner")

# Project only KEYWORDS_NUM column as target schema requires only that column
result = joined[["KEYWORDS_NUM"]].copy()

# Ensure KEYWORDS_NUM is integer type as per target schema
result["KEYWORDS_NUM"] = result["KEYWORDS_NUM"].astype("Int64")

# Save to target CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)