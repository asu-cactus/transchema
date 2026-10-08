import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_6/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_6/training_1.csv", index_col=0)

df0_sub = df0[['committee_name', 'calaccess_committee_id']].copy()
df0_sub['amount'] = 0.0
df0_sub.rename(columns={'committee_name': 'committee_name_x'}, inplace=True)

df1_sub = df1[['committee_name', 'amount']].copy()
df1_sub.rename(columns={'committee_name': 'committee_name_x'}, inplace=True)
df1_sub['amount'] = df1_sub['amount'].astype(float)

result = pd.concat([df0_sub, df1_sub], ignore_index=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_6/target_multisource_mcts.csv", index=False)