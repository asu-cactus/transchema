import pandas as pd

s9_34_9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)
s9_34_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)

joined = pd.merge(s9_34_9, s9_34_3, on="ROW_WID", how="inner")

result = joined.groupby("KEYWORDS_NUM", as_index=False).size().rename(columns={"size": "count"})

# The target schema only has KEYWORDS_NUM column, so we keep unique KEYWORDS_NUM values.
# The target examples show only KEYWORDS_NUM column, so we output unique KEYWORDS_NUM values.
# The GROUP_BY operation implies grouping by KEYWORDS_NUM, but target schema has only KEYWORDS_NUM column.
# So we just output unique KEYWORDS_NUM values.

result = result[["KEYWORDS_NUM"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)