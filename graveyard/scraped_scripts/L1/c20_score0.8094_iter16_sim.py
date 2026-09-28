import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv", index_col=0)

result = df0.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'sum',
    'tip': 'sum',
    'size': 'sum'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)