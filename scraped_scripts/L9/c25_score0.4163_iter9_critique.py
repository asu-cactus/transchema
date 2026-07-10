import pandas as pd

# Read all source tables
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_9.csv", index_col=0)

# UNION the four tables with the same schema
union_df = pd.concat([src0, src1, src4, src5], ignore_index=True)

# JOIN union_df with all other tables on ROW_WID using outer joins to keep all rows
result = union_df.merge(src2, on='ROW_WID', how='outer')
result = result.merge(src3, on='ROW_WID', how='outer')
result = result.merge(src6, on='ROW_WID', how='outer')
result = result.merge(src7, on='ROW_WID', how='outer')
result = result.merge(src8, on='ROW_WID', how='outer')
result = result.merge(src9, on='ROW_WID', how='outer')

# Project CANCEL_DT column (may contain NaNs)
result = result[['CANCEL_DT']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)