import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

df = pd.concat([df0], ignore_index=True)

df = df[['y', 'sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']]

df['y'] = df['y'].astype(int)
df['sepal length (cm)'] = df['sepal length (cm)'].round().astype(int)
df['sepal width (cm)'] = df['sepal width (cm)'].round().astype(int)
df['petal length (cm)'] = df['petal length (cm)'].round().astype(int)
df['petal width (cm)'] = df['petal width (cm)'].round().astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)