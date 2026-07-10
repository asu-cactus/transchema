import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_40/training_0.csv", index_col=0)

result = df0.groupby("school_name", as_index=False)["reading_score"].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_40/target_multisource_mcts.csv", index=False)