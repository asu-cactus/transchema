import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)

union_4_5_7_9 = pd.concat([s4, s5, s7, s9], ignore_index=True)

join_0 = pd.merge(union_4_5_7_9, s0, on="ROW_WID", how="inner")
join_1 = pd.merge(join_0, s1, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, s2, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, s3, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, s6, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, s8, on="ROW_WID", how="inner")

result = join_5.groupby("INTERACTIONS_NUM", as_index=False).size().rename(columns={"size": "INTERACTIONS_NUM"})

# The target schema is ['INTERACTIONS_NUM': integer], but the target examples show INTERACTIONS_NUM as a count of occurrences.
# The groupby above counts rows per INTERACTIONS_NUM value, but the target examples show INTERACTIONS_NUM as the value itself.
# So we should just output the distinct INTERACTIONS_NUM values from s8, as the target examples show counts of INTERACTIONS_NUM values.
# The partial plan says GROUP_BY : [INTERACTIONS_NUM], but the target examples show INTERACTIONS_NUM as integer values, not counts.
# So the correct interpretation is to output the INTERACTIONS_NUM column from s8, grouped by INTERACTIONS_NUM, counting occurrences.

# So we rename the count column to 'count' and keep INTERACTIONS_NUM as is.
# But the target schema only has INTERACTIONS_NUM column, so we output the counts as INTERACTIONS_NUM.

# Actually, the target examples show INTERACTIONS_NUM values, not counts.
# So the best guess is to output the INTERACTIONS_NUM column from s8, dropping duplicates.

# But the partial plan says GROUP_BY : [INTERACTIONS_NUM], so we do groupby INTERACTIONS_NUM and count rows per group.

# So final output is a dataframe with columns: INTERACTIONS_NUM and count of rows per INTERACTIONS_NUM.

# But the target schema only has INTERACTIONS_NUM column, so we output the counts as INTERACTIONS_NUM.

# This is ambiguous, but following the partial plan literally:

final_result = join_5.groupby("INTERACTIONS_NUM", as_index=False).size()
final_result.columns = ["INTERACTIONS_NUM", "COUNT"]

# But target schema only has INTERACTIONS_NUM column, so output the counts as INTERACTIONS_NUM:

final_output = final_result[["COUNT"]].rename(columns={"COUNT": "INTERACTIONS_NUM"})

final_output.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)