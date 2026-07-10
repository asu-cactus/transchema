import pandas as pd

src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)
union_df = pd.concat([src4, src5, src7, src9], ignore_index=True)

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
join1 = pd.merge(union_df, src0, on="ROW_WID", how="inner")

src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
join2 = pd.merge(join1, src1, on="ROW_WID", how="inner")

src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
join3 = pd.merge(join2, src2, on="ROW_WID", how="inner")

src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
join4 = pd.merge(join3, src3, on="ROW_WID", how="inner")

src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
join5 = pd.merge(join4, src6, on="ROW_WID", how="inner")

src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)
final_join = pd.merge(join5, src8, on="ROW_WID", how="inner")

result = final_join.groupby("INTERACTIONS_NUM", as_index=False).size().rename(columns={"size": "INTERACTIONS_NUM"})
# The above line groups by INTERACTIONS_NUM and counts rows per group, but target schema only has INTERACTIONS_NUM column with integer values.
# The target examples show INTERACTIONS_NUM values as integers, so we just output the counts of each INTERACTIONS_NUM value.

# But the target schema is ['INTERACTIONS_NUM': integer], and target examples show INTERACTIONS_NUM values like 64, 56, 65, etc.
# The partial plan says GROUP_BY : [INTERACTIONS_NUM], so the target table is the distinct INTERACTIONS_NUM values with their counts? 
# The target examples show only one column INTERACTIONS_NUM, so likely the target is the distinct INTERACTIONS_NUM values (not counts).
# The example shows 4161 target examples, so likely the target is the distinct INTERACTIONS_NUM values from the data.

# So we just need distinct INTERACTIONS_NUM values from the joined data.

result = final_join[["INTERACTIONS_NUM"]].drop_duplicates().reset_index(drop=True)
result["INTERACTIONS_NUM"] = result["INTERACTIONS_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)