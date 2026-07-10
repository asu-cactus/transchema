import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_4/training_0.csv", index_col=0)

result = df.groupby('fname', as_index=False).agg(count_of_obs=('fname', 'count'))

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts.csv", index=False)