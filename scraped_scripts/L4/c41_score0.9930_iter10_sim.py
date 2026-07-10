import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['label'] = df['label'].astype(str).str.lower().map({'g':1, 'r':1, 'purple':1, 'b':1}).fillna(0).astype(int)

agg = df.groupby('y').agg(
    x_count = ('x', 'count'),
    x_avg = ('x', 'mean'),
    label_count = ('label', 'count')
).reset_index()

agg = agg.rename(columns={'y':'y', 'x_avg':'x', 'label_count':'label'})

agg['x'] = agg['x'].round().astype(int)
agg['label'] = agg['label'].astype(int)
agg['y'] = agg['y'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)