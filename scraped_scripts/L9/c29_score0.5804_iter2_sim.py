import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_7.csv", index_col=0)

joined = pd.merge(source0, source7, on="ROW_WID", how="inner")

result = joined.groupby("COLLECTION_EVENTS_NUM", as_index=False).size().rename(columns={"size": "COUNT"})

final = result[["COLLECTION_EVENTS_NUM"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)