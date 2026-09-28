import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

df = df0[['y', 'sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']].copy()

# Group by 'y' and aggregate other columns by mean
df = df.groupby('y', as_index=False).agg({
    'sepal length (cm)': 'mean',
    'sepal width (cm)': 'mean',
    'petal length (cm)': 'mean',
    'petal width (cm)': 'mean'
})

# Convert all columns to int64 as per target schema
df = df.astype({
    'y': 'int64',
    'sepal length (cm)': 'int64',
    'sepal width (cm)': 'int64',
    'petal length (cm)': 'int64',
    'petal width (cm)': 'int64'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)