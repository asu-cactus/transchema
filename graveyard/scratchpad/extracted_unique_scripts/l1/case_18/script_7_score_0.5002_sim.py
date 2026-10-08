import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)

df_joined = pd.merge(df0, df0, on='y', suffixes=('', '_dup'))

df_joined = df_joined.rename(columns={
    'y': 'y',
    'sepal length (cm)': 'sepal length (cm)',
    'sepal width (cm)': 'sepal width (cm)',
    'petal length (cm)': 'petal length (cm)',
    'petal width (cm)': 'petal width (cm)'
})

target_df = df_joined[['y', 'sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']]

target_df = target_df.astype({
    'y': 'int64',
    'sepal length (cm)': 'int64',
    'sepal width (cm)': 'int64',
    'petal length (cm)': 'int64',
    'petal width (cm)': 'int64'
})

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv")