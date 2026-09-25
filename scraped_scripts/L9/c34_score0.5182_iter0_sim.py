import pandas as pd

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
union_df = pd.concat([s2, s5, s6, s8], ignore_index=True)

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
join_0 = pd.merge(union_df, s0, on="ROW_WID", how="inner")

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
join_1 = pd.merge(join_0, s1, on="ROW_WID", how="inner")

s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
join_2 = pd.merge(join_1, s3, on="ROW_WID", how="inner")

s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
join_3 = pd.merge(join_2, s4, on="ROW_WID", how="inner")

s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
join_4 = pd.merge(join_3, s7, on="ROW_WID", how="inner")

s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)
join_5 = pd.merge(join_4, s9, on="ROW_WID", how="inner")

result = join_5.groupby("KEYWORDS_NUM", as_index=False).size().rename(columns={"size": "KEYWORDS_NUM"})
# The groupby size counts rows per KEYWORDS_NUM, but target schema expects KEYWORDS_NUM as integer column with counts as rows.
# The target schema is ['KEYWORDS_NUM': integer], and target examples show KEYWORDS_NUM values, not counts.
# So the groupby should produce unique KEYWORDS_NUM values, but target examples show counts of rows per KEYWORDS_NUM.
# Actually, the target examples show KEYWORDS_NUM values, not counts. So the groupby should produce unique KEYWORDS_NUM values.
# The partial plan says GROUP_BY : [KEYWORDS_NUM], so we just group by KEYWORDS_NUM and count rows per group.
# The target schema is ['KEYWORDS_NUM': integer], so the output should be a single column KEYWORDS_NUM with counts.
# But the target examples show KEYWORDS_NUM values, not counts.
# So the groupby size is the count of rows per KEYWORDS_NUM, but the target expects the KEYWORDS_NUM values themselves.
# So the output should be the unique KEYWORDS_NUM values, not counts.
# Therefore, just output unique KEYWORDS_NUM values as integers.
result = join_5[["KEYWORDS_NUM"]].drop_duplicates().sort_values("KEYWORDS_NUM").reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)