import pandas as pd

# Read all source tables
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_9.csv", index_col=0)

# Union the four large tables with the same schema
union_df = pd.concat([src2, src3, src6, src8], ignore_index=True)

# Join unioned table with all other source tables on ROW_WID
df = union_df.merge(src0, on='ROW_WID', how='inner')
df = df.merge(src1, on='ROW_WID', how='inner')
df = df.merge(src4, on='ROW_WID', how='inner')
df = df.merge(src5, on='ROW_WID', how='inner')
df = df.merge(src7, on='ROW_WID', how='inner')
df = df.merge(src9, on='ROW_WID', how='inner')

# Output only the MONTHS_AGE column as per target schema
df[['MONTHS_AGE']].to_csv("autopipeline-benchmarks/github-pipelines/length9_23/target_multisource_mcts.csv", index=False)