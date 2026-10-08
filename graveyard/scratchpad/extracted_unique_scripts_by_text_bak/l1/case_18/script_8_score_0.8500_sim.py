import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on='y', suffixes=('_left', '_right'))

grouped = joined.groupby('y').agg({
    'sepal length (cm)_left': 'sum',
    'sepal width (cm)_left': 'sum',
    'petal length (cm)_left': 'sum',
    'petal width (cm)_left': 'sum',
}).reset_index()

grouped.columns = ['y', 'sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']

grouped = grouped.astype({
    'y': int,
    'sepal length (cm)': int,
    'sepal width (cm)': int,
    'petal length (cm)': int,
    'petal width (cm)': int,
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)