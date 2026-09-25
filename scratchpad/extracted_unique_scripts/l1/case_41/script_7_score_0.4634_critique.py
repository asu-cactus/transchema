import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

grouped = df0.groupby(['zipcode', 'AGI_STUB'], as_index=False).agg({
    'N1': 'sum',
    'A00100': 'sum'
})

grouped = grouped.astype({
    'zipcode': 'int64',
    'AGI_STUB': 'int64',
    'N1': 'int64',
    'A00100': 'int64'
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)