import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

dog_type_cols = ['doggo', 'floofer', 'pupper', 'puppo']

counts = df0[dog_type_cols].notnull().sum()

result = counts.to_frame(name='dog_type').reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)