import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_94/training_0.csv", index_col=0)

result = pd.DataFrame({
    '0': [df0['0'].mean()],
    '1': [df0['1'].mean()],
    '2': [df0['2'].mean()],
    '3': [df0['3'].mean()]
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_94/target_multisource_mcts.csv", index=False)