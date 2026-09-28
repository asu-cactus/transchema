import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_1/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_1/training_0.csv", index_col=0)

result = pd.concat([df0, df1], ignore_index=True)

result = result.astype({'userId': 'int64', 'movieId': 'int64', 'rating': 'float64', 'timestamp': 'int64'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_1/target_multisource_mcts.csv", index=False)