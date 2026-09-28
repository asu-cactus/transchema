import pandas as pd

# Load all source files
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

# UNION sources with the same schema: src2, src5, src6, src8
unioned_dim = pd.concat([src2, src5, src6, src8], ignore_index=True)

# Join unioned_dim with src0 on ROW_WID
result = pd.merge(unioned_dim, src0, on='ROW_WID', how='inner')

# Join with src1
result = pd.merge(result, src1, on='ROW_WID', how='inner')

# Join with src3
result = pd.merge(result, src3, on='ROW_WID', how='inner')

# Join with src4
result = pd.merge(result, src4, on='ROW_WID', how='inner')

# Join with src7
result = pd.merge(result, src7, on='ROW_WID', how='inner')

# Join with src9
result = pd.merge(result, src9, on='ROW_WID', how='inner')

# Project only KEYWORDS_NUM column
result = result[['KEYWORDS_NUM']]

# Drop duplicates to get distinct KEYWORDS_NUM values
result = result.drop_duplicates().reset_index(drop=True)

# Ensure KEYWORDS_NUM is integer type
result['KEYWORDS_NUM'] = result['KEYWORDS_NUM'].astype(int)

# Save to target CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)