import pandas as pd

source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_3.csv", index_col=0)

joined = pd.merge(source2, source3, on="TrackID", how="inner", suffixes=('_2', '_3'))

result = joined.groupby("TrackID", as_index=False).size().loc[:, ["TrackID"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_88/target_multisource_mcts.csv", index=False)