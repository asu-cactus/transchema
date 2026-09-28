import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_7/training_1.csv", index_col=0)

df_target = df1[['contributor_firstname', 'contributor_lastname', 'amount']].copy()
df_target['contributor_firstname'] = df_target['contributor_firstname'].astype(str)
df_target['contributor_lastname'] = df_target['contributor_lastname'].astype(str)
df_target['amount'] = df_target['amount'].astype(float)

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length2_7/target_multisource_mcts.csv", index=False)