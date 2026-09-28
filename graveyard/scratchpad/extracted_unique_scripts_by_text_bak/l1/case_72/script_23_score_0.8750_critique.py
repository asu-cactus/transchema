import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv", index_col=0)
result = df.groupby('condition', as_index=False)['click'].sum()
result.columns = ['condition', '0']
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)