import pandas as pd

# Read all source tables
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)

# UNION the four large tables with the same schema
union_0 = pd.concat([src0, src1, src8, src9], ignore_index=True)

# Join union_0 with src2 on ROW_WID
joined_1 = pd.merge(union_0, src2, on='ROW_WID', how='inner')

# Join with src3
joined_2 = pd.merge(joined_1, src3, on='ROW_WID', how='inner')

# Join with src4 (contains TECHSUPPORT_NUM)
joined_3 = pd.merge(joined_2, src4, on='ROW_WID', how='inner')

# Join with src5
joined_4 = pd.merge(joined_3, src5, on='ROW_WID', how='inner')

# Join with src6
joined_5 = pd.merge(joined_4, src6, on='ROW_WID', how='inner')

# Join with src7
joined_6 = pd.merge(joined_5, src7, on='ROW_WID', how='inner')

# Project only TECHSUPPORT_NUM and convert to int
result = joined_6[['TECHSUPPORT_NUM']].copy()
result['TECHSUPPORT_NUM'] = result['TECHSUPPORT_NUM'].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)