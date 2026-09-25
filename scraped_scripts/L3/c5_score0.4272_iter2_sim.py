import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_5/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_5/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_5/training_2.csv", index_col=0)

df_all = pd.concat([df0, df1, df2], ignore_index=True)

agg = df_all.groupby('quality').agg({
    'fixed acidity': 'mean',
    'volatile acidity': 'mean',
    'citric acid': 'mean',
    'residual sugar': 'mean',
    'chlorides': 'mean',
    'density': 'mean',
    'pH': 'mean',
    'sulphates': 'mean',
    'alcohol': 'mean',
    'free sulfur dioxide': 'mean',
    'total sulfur dioxide': 'mean'
}).reset_index()

agg['free sulfur dioxide'] = agg['free sulfur dioxide'].round().astype(int)
agg['total sulfur dioxide'] = agg['total sulfur dioxide'].round().astype(int)
agg['quality'] = agg['quality'].astype(int)

cols_order = ['fixed acidity', 'volatile acidity', 'citric acid', 'residual sugar', 'chlorides',
              'free sulfur dioxide', 'total sulfur dioxide', 'density', 'pH', 'sulphates', 'alcohol', 'quality']

Target3_5 = agg[cols_order]

Target3_5.to_csv("autopipeline-benchmarks/github-pipelines/length3_5/target_multisource_mcts.csv", index=False)