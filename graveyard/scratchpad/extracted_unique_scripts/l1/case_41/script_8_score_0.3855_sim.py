import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

result = df[['zipcode', 'AGI_STUB', 'N1', 'A00100']].copy()
result = result.astype({'zipcode': 'int64', 'AGI_STUB': 'int64', 'N1': 'int64', 'A00100': 'int64'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)