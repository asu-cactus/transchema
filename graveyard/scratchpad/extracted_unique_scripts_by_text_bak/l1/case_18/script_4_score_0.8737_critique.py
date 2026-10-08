import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

agg = df0.groupby('y').agg({
    'sepal length (cm)': 'sum',
    'sepal width (cm)': 'sum',
    'petal length (cm)': 'sum',
    'petal width (cm)': 'sum'
}).reset_index()

agg = agg.astype({
    'y': 'int64',
    'sepal length (cm)': 'int64',
    'sepal width (cm)': 'int64',
    'petal length (cm)': 'int64',
    'petal width (cm)': 'int64'
})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)