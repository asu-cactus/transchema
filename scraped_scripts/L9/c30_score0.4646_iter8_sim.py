import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_2.csv", index_col=0)

join_01 = pd.merge(source0, source1, on="ROW_WID", how="inner")
join_012 = pd.merge(join_01, source2, on="ROW_WID", how="inner")

count_techsupport = join_012["TECHSUPPORT_NUM"].count()
avg_visits = join_012["VISITS_NUM"].mean()
sum_keywords = join_012["KEYWORDS_NUM"].sum()

# The target schema is ['ARPU': float] and target examples show float values like 630.00, 433.14, 665.00
# The partial plan suggests aggregations but no group_by keys, so the result is a single-row aggregation.
# However, the target examples show multiple rows with ARPU values, so the aggregation alone is insufficient.
# The target examples have 4161 rows with ARPU values, which appear to come from source tables 3,4,5,7 (all have ARPU column).
# These sources have the same schema and contain ARPU values.
# So we must union these ARPU-containing sources to produce the final target table.

source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_5.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_7.csv", index_col=0)

arpu_frames = [source3[['ARPU']], source4[['ARPU']], source5[['ARPU']], source7[['ARPU']]]
target_df = pd.concat(arpu_frames, ignore_index=True)

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_30/target_multisource_mcts.csv", index=False)