import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

grouped = df0.groupby('y').agg({
    'sepal length (cm)': 'count',
    'sepal width (cm)': 'count',
    'petal length (cm)': 'count',
    'petal width (cm)': 'count'
}).reset_index()

for col in ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']:
    grouped[col] = grouped[col].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)