import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_5/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_5/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_5/training_2.csv", index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

df = df.astype({
    'fixed acidity': float,
    'volatile acidity': float,
    'citric acid': float,
    'residual sugar': float,
    'chlorides': float,
    'free sulfur dioxide': 'Int64',
    'total sulfur dioxide': 'Int64',
    'density': float,
    'pH': float,
    'sulphates': float,
    'alcohol': float,
    'quality': 'Int64'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_5/target_multisource_mcts.csv", index=False)