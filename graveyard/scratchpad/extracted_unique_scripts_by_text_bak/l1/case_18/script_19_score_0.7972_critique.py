import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)

# Group by 'y' and aggregate by mean for the other columns
target_df = df0.groupby('y', as_index=False).agg({
    'sepal length (cm)': 'mean',
    'sepal width (cm)': 'mean',
    'petal length (cm)': 'mean',
    'petal width (cm)': 'mean'
})

# Convert all columns to int64 as per target schema
target_df = target_df.astype({
    'y': 'int64',
    'sepal length (cm)': 'int64',
    'sepal width (cm)': 'int64',
    'petal length (cm)': 'int64',
    'petal width (cm)': 'int64'
})

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)