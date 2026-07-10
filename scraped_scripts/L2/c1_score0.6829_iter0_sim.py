import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_1/training_0.csv", index_col=0)

df = pd.concat([df0], ignore_index=True)

df = df.astype({
    'userId': 'int64',
    'movieId': 'int64',
    'rating': 'float64',
    'timestamp': 'int64'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_1/target_multisource_mcts.csv", index=False)