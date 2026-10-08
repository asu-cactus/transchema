import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)

union_0_1_8_9 = pd.concat([s0, s1, s8, s9], ignore_index=True)

s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)

df = union_0_1_8_9.merge(s4, on="ROW_WID", how="inner") \
                  .merge(s2, on="ROW_WID", how="inner") \
                  .merge(s3, on="ROW_WID", how="inner") \
                  .merge(s5, on="ROW_WID", how="inner") \
                  .merge(s6, on="ROW_WID", how="inner") \
                  .merge(s7, on="ROW_WID", how="inner")

result = df.groupby("TECHSUPPORT_NUM", as_index=False).size().rename(columns={"size": "count"})

# The target schema only requires TECHSUPPORT_NUM column, so we select distinct TECHSUPPORT_NUM values
# The target examples show TECHSUPPORT_NUM as integer, so ensure dtype is int
final = df[["TECHSUPPORT_NUM"]].drop_duplicates().copy()
final["TECHSUPPORT_NUM"] = final["TECHSUPPORT_NUM"].astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)