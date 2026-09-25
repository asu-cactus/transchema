import pandas as pd

src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)
union_0 = pd.concat([src4, src5, src7, src9], ignore_index=True)

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
join_1 = pd.merge(union_0, src0, on="ROW_WID", how="inner")

src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
join_2 = pd.merge(join_1, src1, on="ROW_WID", how="inner")

src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
join_3 = pd.merge(join_2, src2, on="ROW_WID", how="inner")

src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
join_4 = pd.merge(join_3, src3, on="ROW_WID", how="inner")

src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
join_5 = pd.merge(join_4, src6, on="ROW_WID", how="inner")

src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)
join_6 = pd.merge(join_5, src8, on="ROW_WID", how="inner")

result = join_6[["INTERACTIONS_NUM"]].groupby("INTERACTIONS_NUM", as_index=False).size()
result.columns = ["INTERACTIONS_NUM", "count"]
result = result[["INTERACTIONS_NUM"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)