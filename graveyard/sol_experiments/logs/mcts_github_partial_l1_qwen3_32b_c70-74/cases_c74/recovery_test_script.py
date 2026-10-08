import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_74/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_74/test_1.csv', index_col=0)

df0_renamed = df0.rename(columns={'committee_name': 'committee_name_x'})
df1_renamed = df1.rename(columns={'committee_name': 'committee_name_y'})

joined = pd.merge(df0_renamed, df1_renamed, on='calaccess_committee_id')
joined.to_csv('autopipeline-benchmarks/github-pipelines/length1_74/target_multisource_mcts_recovery_test_val.csv', index=False)