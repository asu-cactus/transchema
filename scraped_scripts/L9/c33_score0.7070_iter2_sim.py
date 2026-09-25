import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)

join_0_1 = pd.merge(source0, source1, on="ROW_WID", how="inner")
join_1_2 = pd.merge(join_0_1, source2, on="ROW_WID", how="inner")
join_2_3 = pd.merge(join_1_2, source3, on="ROW_WID", how="inner")
join_3_6 = pd.merge(join_2_3, source6, on="ROW_WID", how="inner")
join_6_8 = pd.merge(join_3_6, source8, on="ROW_WID", how="inner")

result = join_6_8[["INTERACTIONS_NUM"]].copy()
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)