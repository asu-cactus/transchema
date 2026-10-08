import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

grouped = df0.groupby('y').agg({
    'sepal length (cm)': 'mean',
    'sepal width (cm)': 'mean',
    'petal length (cm)': 'mean',
    'petal width (cm)': 'mean',
}).reset_index()

grouped = grouped.astype({
    'y': int,
    'sepal length (cm)': int,
    'sepal width (cm)': int,
    'petal length (cm)': int,
    'petal width (cm)': int,
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)