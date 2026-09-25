import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

# Group by 'y' and count the number of rows per group for each measurement column
df = df0.groupby('y').agg({
    'sepal length (cm)': 'count',
    'sepal width (cm)': 'count',
    'petal length (cm)': 'count',
    'petal width (cm)': 'count'
}).reset_index()

# Convert all columns to int as per target schema
df = df.astype({
    'y': int,
    'sepal length (cm)': int,
    'sepal width (cm)': int,
    'petal length (cm)': int,
    'petal width (cm)': int
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)