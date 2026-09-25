import pandas as pd

# Read dimension tables with same schema
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_4.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_8.csv", index_col=0)

# Union dimension tables
union_dim = pd.concat([src2, src3, src4, src8], ignore_index=True)

# Read aspect tables
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_1.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_7.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_9.csv", index_col=0)

# Join union_dim with all aspect tables on ROW_WID
result = union_dim.merge(src0, on='ROW_WID', how='inner')
result = result.merge(src1, on='ROW_WID', how='inner')
result = result.merge(src5, on='ROW_WID', how='inner')
result = result.merge(src6, on='ROW_WID', how='inner')
result = result.merge(src7, on='ROW_WID', how='inner')
result = result.merge(src9, on='ROW_WID', how='inner')

# Project CANCEL_DT column
target = result[['CANCEL_DT']]

# Write output
target.to_csv("autopipeline-benchmarks/github-pipelines/length9_26/target_multisource_mcts.csv", index=False)