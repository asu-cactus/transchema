import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_2.csv", index_col=0)

agg = source1.groupby("movie_id")["rating"].count().reset_index()
agg.columns = ["movie_id", "0"]
agg["movie_id"] = agg["movie_id"].astype(int)
agg["0"] = agg["0"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_93/target_multisource_mcts.csv", index=False)