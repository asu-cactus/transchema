import pandas as pd

# Read source tables with primary structured data
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/test_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/test_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/test_3.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/test_9.csv", index_col=0)

# UNION: Combine all structured data sources with same schema
base = pd.concat([df0, df2, df3, df9], ignore_index=True)

# GROUP BY to ensure unique ROW_WID (target has unique ROW_WID constraints)
base = base.groupby("ROW_WID", as_index=False).first()

# JOIN: Merge in auxiliary count-based source tables
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/test_1.csv", index_col=0)
df = pd.merge(base, s1, on="ROW_WID", how="left")

s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/test_4.csv", index_col=0)
df = pd.merge(df, s4, on="ROW_WID", how="left")

s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/test_5.csv", index_col=0)
df = pd.merge(df, s5, on="ROW_WID", how="left")

s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/test_6.csv", index_col=0)
df = pd.merge(df, s6, on="ROW_WID", how="left")

s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/test_7.csv", index_col=0)
df = pd.merge(df, s7, on="ROW_WID", how="left")

s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/test_8.csv", index_col=0)
df = pd.merge(df, s8, on="ROW_WID", how="left")

# Write the final merged table to target CSV
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_27/target_multisource_mcts_recovery_test_val.csv", index=False)