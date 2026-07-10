import pandas as pd

# Read and union dimension tables with identical schema
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)
union_0 = pd.concat([src4, src5, src7, src9], ignore_index=True)

# Read aspect tables
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)

# Join all on ROW_WID using inner joins
join_1 = pd.merge(union_0, src0, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, src1, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, src2, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, src3, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, src6, on="ROW_WID", how="inner")
join_6 = pd.merge(join_5, src8, on="ROW_WID", how="inner")

# Project only INTERACTIONS_NUM as target schema requires
result = join_6[["INTERACTIONS_NUM"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)