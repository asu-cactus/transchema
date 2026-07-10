import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

agg_df = df0.groupby('y').mean().reset_index()

agg_df['sepal length (cm)'] = agg_df['sepal length (cm)'].astype(int)
agg_df['sepal width (cm)'] = agg_df['sepal width (cm)'].astype(int)
agg_df['petal length (cm)'] = agg_df['petal length (cm)'].astype(int)
agg_df['petal width (cm)'] = agg_df['petal width (cm)'].astype(int)
agg_df['y'] = agg_df['y'].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)