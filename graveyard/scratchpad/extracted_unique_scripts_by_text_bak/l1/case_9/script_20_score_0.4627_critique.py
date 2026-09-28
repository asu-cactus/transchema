import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_9/training_0.csv", index_col=0)

result = df.groupby(['zipcode', 'AGI_STUB'], as_index=False).agg({'N1': 'sum', 'A00100': 'sum'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts.csv", index=False)