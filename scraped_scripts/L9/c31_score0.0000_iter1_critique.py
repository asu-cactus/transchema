import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_3.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_5.csv", index_col=0)

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_4.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_9.csv", index_col=0)

# Join the four large source tables on ROW_WID (inner join to avoid duplicates and NaNs)
join_01 = pd.merge(s0, s1, on="ROW_WID", how="inner", suffixes=('_0', '_1'))
join_013 = pd.merge(join_01, s3, on="ROW_WID", how="inner", suffixes=('', '_3'))
join_0135 = pd.merge(join_013, s5, on="ROW_WID", how="inner", suffixes=('', '_5'))

# After these joins, columns HOME_PASSED_0, HOME_PASSED_1, HOME_PASSED, HOME_PASSED_5 exist.
# According to Hint 1, the target has only one HOME_PASSED column, so we must decide which to keep.
# Since these tables have the same schema, and presumably the same HOME_PASSED per ROW_WID,
# we can take HOME_PASSED from s0 (HOME_PASSED_0) or any of them.
# We'll take HOME_PASSED_0.

# Join with aspect tables on ROW_WID
join_2 = pd.merge(join_0135, s2, on="ROW_WID", how="inner")
join_4 = pd.merge(join_2, s4, on="ROW_WID", how="inner")
join_6 = pd.merge(join_4, s6, on="ROW_WID", how="inner")
join_7 = pd.merge(join_6, s7, on="ROW_WID", how="inner")
join_8 = pd.merge(join_7, s8, on="ROW_WID", how="inner")
join_9 = pd.merge(join_8, s9, on="ROW_WID", how="inner")

# Project HOME_PASSED from s0 (HOME_PASSED_0)
result = join_9[["HOME_PASSED_0"]].copy()
result.columns = ["HOME_PASSED"]
result["HOME_PASSED"] = result["HOME_PASSED"].astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)