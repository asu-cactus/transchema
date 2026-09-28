import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_80/training_0.csv", index_col=0)

count_0 = df0['0'].count()
count_1 = df0['1'].count()

result = pd.DataFrame({
    '0': [float(count_0)],
    '1': [float(count_1)],
    '2': [float('nan')],
    '3': [float('nan')]
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_80/target_multisource_mcts.csv", index=False)