import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, left_on="sepal length (cm)", right_on="sepal length (cm)", suffixes=('', '_dup'))

agg = df_joined.groupby('y').agg({
    'sepal length (cm)': 'sum',
    'sepal width (cm)': 'sum',
    'petal length (cm)': 'sum',
    'petal width (cm)': 'sum'
}).reset_index()

for col in ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']:
    agg[col] = agg[col].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)