import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

df = pd.concat([df0], ignore_index=True)

df = df[['y', 'sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']]

df = df.astype({
    'y': 'int64',
    'sepal length (cm)': 'int64',
    'sepal width (cm)': 'int64',
    'petal length (cm)': 'int64',
    'petal width (cm)': 'int64'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)