import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

grouped = df0.groupby(['zipcode', 'AGI_STUB'], as_index=False).agg(
    N1=('N1', 'count'),
    A00100=('A00100', 'mean')
)

grouped['N1'] = grouped['N1'].astype(int)
grouped['A00100'] = grouped['A00100'].round().astype(int)
grouped['zipcode'] = grouped['zipcode'].astype(int)
grouped['AGI_STUB'] = grouped['AGI_STUB'].astype(int)

grouped = grouped[['zipcode', 'AGI_STUB', 'N1', 'A00100']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)