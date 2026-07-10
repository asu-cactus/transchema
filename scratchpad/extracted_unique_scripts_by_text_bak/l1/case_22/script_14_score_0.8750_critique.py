import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_22/training_0.csv", index_col=0)

result = df0.groupby('condition', as_index=False)['click'].sum()

result = result.astype({'condition': int, 'click': int})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)