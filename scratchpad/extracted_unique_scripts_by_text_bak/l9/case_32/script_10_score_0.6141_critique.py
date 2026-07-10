import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_9.csv", index_col=0)

# UNION the dimension tables with identical schema
union_5678 = pd.concat([s5, s6, s7, s8], ignore_index=True)

# JOIN unioned dimension table with aspect tables on ROW_WID
join_56780 = pd.merge(union_5678, s0, on="ROW_WID", how="inner")
join_567801 = pd.merge(join_56780, s1, on="ROW_WID", how="inner")
join_5678012 = pd.merge(join_567801, s2, on="ROW_WID", how="inner")
join_56780123 = pd.merge(join_5678012, s3, on="ROW_WID", how="inner")
join_567801234 = pd.merge(join_56780123, s4, on="ROW_WID", how="inner")
join_all = pd.merge(join_567801234, s9, on="ROW_WID", how="inner")

# Select VISITS_NUM column as target schema requires
final = join_all[["VISITS_NUM"]].drop_duplicates().reset_index(drop=True)
final["VISITS_NUM"] = final["VISITS_NUM"].astype(int)

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)