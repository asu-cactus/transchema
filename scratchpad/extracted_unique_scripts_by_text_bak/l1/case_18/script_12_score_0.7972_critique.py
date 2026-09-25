import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

# Group by 'y' and aggregate other columns by mean
df_grouped = df0.groupby('y', as_index=False).agg({
    'sepal length (cm)': 'mean',
    'sepal width (cm)': 'mean',
    'petal length (cm)': 'mean',
    'petal width (cm)': 'mean'
})

# Convert aggregated float columns to int as per target schema
df_grouped = df_grouped.astype({
    'y': 'int64',
    'sepal length (cm)': 'int64',
    'sepal width (cm)': 'int64',
    'petal length (cm)': 'int64',
    'petal width (cm)': 'int64'
})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)