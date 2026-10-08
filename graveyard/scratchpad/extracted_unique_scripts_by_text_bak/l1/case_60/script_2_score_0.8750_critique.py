import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_60/training_0.csv", index_col=0)

df = df0.copy()

df = df[df['type'] == 'Urban']

result = df.groupby('type', as_index=False)['driver_count'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)