import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_54/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

grouped = df.groupby("condition", as_index=False).agg({"click": "sum"})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_54/target_multisource_mcts.csv", index=False)