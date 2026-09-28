import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_80/training_0.csv", index_col=0)

result = df0.agg({
    '0': 'mean',
    '1': 'mean',
    '2': 'mean',
    '3': 'mean'
}).to_frame().T

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_80/target_multisource_mcts.csv", index=False)