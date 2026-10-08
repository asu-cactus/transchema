import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on='y', suffixes=('_left', '_right'))

df_unpivot = pd.melt(df_joined, id_vars=['y'], 
                     value_vars=['sepal length (cm)_left', 'sepal width (cm)_left', 'petal length (cm)_left', 'petal width (cm)_left'],
                     var_name='feature', value_name='value')

df_unpivot['feature'] = df_unpivot['feature'].str.replace('_left', '')

df_pivot = df_unpivot.pivot_table(index='y', columns='feature', values='value', aggfunc='mean').reset_index()

df_pivot = df_pivot.rename_axis(None, axis=1)

df_pivot = df_pivot.astype({
    'y': int,
    'sepal length (cm)': int,
    'sepal width (cm)': int,
    'petal length (cm)': int,
    'petal width (cm)': int
})

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)