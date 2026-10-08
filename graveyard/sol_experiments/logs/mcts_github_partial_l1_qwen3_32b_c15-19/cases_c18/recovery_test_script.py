import pandas as pd

source_path = 'autopipeline-benchmarks/github-pipelines/length1_18/test_0.csv'
df = pd.read_csv(source_path, index_col=0)
result = df.groupby('y').agg(
    sepal_length=('sepal length (cm)', 'size'),
    sepal_width=('sepal width (cm)', 'size'),
    petal_length=('petal length (cm)', 'size'),
    petal_width=('petal width (cm)', 'size')
).reset_index()
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts_recovery_test_val.csv', index=False)