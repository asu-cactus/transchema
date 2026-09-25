import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_7/training_1.csv", index_col=0)

df = df1[['contributor_firstname', 'contributor_lastname', 'amount']]

df_grouped = df.groupby('contributor_lastname', as_index=False).agg({
    'contributor_firstname': 'first',
    'amount': 'sum'
})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_7/target_multisource_mcts.csv", index=False)