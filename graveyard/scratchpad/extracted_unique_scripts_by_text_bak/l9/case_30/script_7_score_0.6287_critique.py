import pandas as pd

# Read all source tables
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_9.csv", index_col=0)

# UNION the dimension tables with same schema
unioned_dim = pd.concat([src3, src4, src5, src7], ignore_index=True)

# Join all other source tables on ROW_WID
result = unioned_dim.merge(src0, on='ROW_WID', how='inner')
result = result.merge(src1, on='ROW_WID', how='inner')
result = result.merge(src2, on='ROW_WID', how='inner')
result = result.merge(src6, on='ROW_WID', how='inner')
result = result.merge(src8, on='ROW_WID', how='inner')
result = result.merge(src9, on='ROW_WID', how='inner')

# Project only ARPU column as per target schema
result = result[['ARPU']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_30/target_multisource_mcts.csv", index=False)