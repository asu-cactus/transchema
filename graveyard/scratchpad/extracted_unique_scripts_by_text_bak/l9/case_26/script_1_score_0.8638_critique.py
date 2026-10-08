import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_9.csv", index_col=0)

# UNION the dimension tables with same schema
unioned_dim = pd.concat([s2, s3, s4, s8], ignore_index=True)

# Join unioned_dim with all other tables on ROW_WID
df = unioned_dim.merge(s0, on="ROW_WID", how="inner") \
                 .merge(s1, on="ROW_WID", how="inner") \
                 .merge(s5, on="ROW_WID", how="inner") \
                 .merge(s6, on="ROW_WID", how="inner") \
                 .merge(s7, on="ROW_WID", how="inner") \
                 .merge(s9, on="ROW_WID", how="inner")

# Project only CANCEL_DT column as per target schema
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_26/target_multisource_mcts.csv", index=False, columns=["CANCEL_DT"])