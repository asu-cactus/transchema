import pandas as pd

df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)
union_df = pd.concat([df4, df5, df7, df9], ignore_index=True)

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
join1 = pd.merge(union_df, df0, on="ROW_WID", how="inner")

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
join2 = pd.merge(join1, df1, on="ROW_WID", how="inner")

df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
join3 = pd.merge(join2, df2, on="ROW_WID", how="inner")

df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
join4 = pd.merge(join3, df3, on="ROW_WID", how="inner")

df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
join5 = pd.merge(join4, df6, on="ROW_WID", how="inner")

df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)
final_join = pd.merge(join5, df8, on="ROW_WID", how="inner")

result = final_join.groupby("INTERACTIONS_NUM", as_index=False).size().rename(columns={"size": "INTERACTIONS_NUM_count"})

# The target schema is ['INTERACTIONS_NUM'] with integer values, and target examples show counts of INTERACTIONS_NUM values.
# The partial plan says GROUP_BY : [INTERACTIONS_NUM], so the target is the grouped INTERACTIONS_NUM values with their counts.
# But the target schema only has INTERACTIONS_NUM column, so we output the INTERACTIONS_NUM values repeated as many times as counts.
# However, the target examples show INTERACTIONS_NUM values and their counts (e.g. 105, 83, 228), so likely the target is the grouped INTERACTIONS_NUM values with counts as rows.
# The target schema is ['INTERACTIONS_NUM': integer], so we output the INTERACTIONS_NUM values repeated count times (i.e., explode counts).
# But the target examples show counts as values, so the target is just the INTERACTIONS_NUM values with their counts as rows.
# Since the target schema only has INTERACTIONS_NUM column, we output the INTERACTIONS_NUM values repeated count times.
# To match the target examples, we output the INTERACTIONS_NUM values repeated count times.

# So we repeat each INTERACTIONS_NUM value by its count to get the final table with one column INTERACTIONS_NUM.

expanded = result.loc[result.index.repeat(result["INTERACTIONS_NUM_count"])].copy()
expanded = expanded[["INTERACTIONS_NUM"]].reset_index(drop=True)

expanded.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)