import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_9/training_0.csv", index_col=0)

result = df0.groupby(['zipcode', 'AGI_STUB'], as_index=False)[['N1', 'A00100']].sum()

result = result.astype({'zipcode': 'int64', 'AGI_STUB': 'int64', 'N1': 'int64', 'A00100': 'int64'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts.csv", index=False)