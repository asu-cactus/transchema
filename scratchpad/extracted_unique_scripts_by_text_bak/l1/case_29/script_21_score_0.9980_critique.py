import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)
result = df.groupby('Gender').agg({'Purchase ID': 'count'}).reset_index()
result.columns = ['Gender', '0']
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)