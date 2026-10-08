import pandas as pd

# Load all source tables
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_9.csv", index_col=0)

# UNION sources 5,6,7,8 (same schema)
union_5_6_7_8 = pd.concat([src5, src6, src7, src8], ignore_index=True)

# JOIN unioned table with other sources on ROW_WID
joined = union_5_6_7_8.merge(src0, on='ROW_WID', how='left') \
                     .merge(src1, on='ROW_WID', how='left') \
                     .merge(src2, on='ROW_WID', how='left') \
                     .merge(src3, on='ROW_WID', how='left') \
                     .merge(src4, on='ROW_WID', how='left') \
                     .merge(src9, on='ROW_WID', how='left')

# FILTER rows where VISITS_NUM is not null
filtered = joined[joined['VISITS_NUM'].notna()]

# PROJECT only VISITS_NUM column, convert to integer type
result = filtered[['VISITS_NUM']].copy()
result['VISITS_NUM'] = result['VISITS_NUM'].astype(int)

# Save the result
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)