import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv", index_col=0)

agg = df0.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'min',
    'tip': 'min',
    'size': 'min'
})

agg = agg[['sex', 'smoker', 'total_bill', 'tip', 'size']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)