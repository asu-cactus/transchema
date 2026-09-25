import pandas as pd

s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
union_result = pd.concat([s5, s6, s8], ignore_index=True)

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
join_result_1 = pd.merge(union_result, s0, on="ROW_WID", how="inner")

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
join_result_2 = pd.merge(join_result_1, s1, on="ROW_WID", how="inner")

s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
join_result_3 = pd.merge(join_result_2, s3, on="ROW_WID", how="inner")

s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
join_result_4 = pd.merge(join_result_3, s4, on="ROW_WID", how="inner")

s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
join_result_5 = pd.merge(join_result_4, s7, on="ROW_WID", how="inner")

s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)
final_join = pd.merge(join_result_5, s9, on="ROW_WID", how="inner")

result = final_join.groupby("KEYWORDS_NUM", as_index=False).size().rename(columns={"size": "KEYWORDS_NUM"})
# The above line produces a count per KEYWORDS_NUM, but target schema is just KEYWORDS_NUM integer values.
# The target examples show KEYWORDS_NUM as integer values, not counts.
# So we need to produce a table with unique KEYWORDS_NUM values, each appearing once.
# The partial plan says GROUP_BY : [KEYWORDS_NUM], so likely the target is distinct KEYWORDS_NUM values.
# So we just select distinct KEYWORDS_NUM values.

result = final_join[["KEYWORDS_NUM"]].drop_duplicates().reset_index(drop=True)
result["KEYWORDS_NUM"] = result["KEYWORDS_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)