import pandas as pd

source_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
source_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
source_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
source_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
source_4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
source_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
source_6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
source_7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
source_8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
source_9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

joined = pd.merge(source_9, source_1, on="ROW_WID", how="inner")

result = joined.groupby("KEYWORDS_NUM", as_index=False).size().rename(columns={"size": "KEYWORDS_NUM"})

# The target schema is ['KEYWORDS_NUM': integer], and the target examples show KEYWORDS_NUM as integer values.
# The groupby size counts occurrences per KEYWORDS_NUM, but the target examples show KEYWORDS_NUM as the grouping key, not counts.
# So the groupby should just produce unique KEYWORDS_NUM values, not counts.
# Reconsider: The partial plan says GROUP_BY : [KEYWORDS_NUM], but no aggregation specified.
# The target examples show KEYWORDS_NUM values, no counts.
# So the final output is just the distinct KEYWORDS_NUM values from the join.

result = joined[["KEYWORDS_NUM"]].drop_duplicates().sort_values("KEYWORDS_NUM").reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)