import pandas as pd

source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_1.csv", index_col=0)
result = source1.groupby("movie_id", as_index=False)["rating"].mean()
result.columns = ["movie_id", "0"]
result["0"] = result["0"].round().astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_93/target_multisource_mcts.csv", index=False)