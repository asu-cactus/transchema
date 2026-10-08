import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['label'] = pd.to_numeric(df['label'], errors='coerce')

agg = df.groupby('y').agg(
    x_count=('x', 'count'),
    x_min=('x', 'min'),
    label_max=('label', 'max')
).reset_index()

result = agg.rename(columns={'x_min': 'x', 'y': 'y', 'label_max': 'label'})

result['x'] = result['x'].astype(float)
result['y'] = result['y'].astype(int)
result['label'] = result['label'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_40/target_multisource_mcts.csv", index=False)