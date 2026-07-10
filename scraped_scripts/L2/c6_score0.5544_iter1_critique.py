import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_6/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_6/training_1.csv", index_col=0)

# Rename committee_name to committee_name_x to match target schema
df0.rename(columns={'committee_name': 'committee_name_x'}, inplace=True)

# Join on calaccess_committee_id
joined = pd.merge(df0[['committee_name_x', 'calaccess_committee_id']], 
                  df1[['calaccess_committee_id', 'amount']], 
                  on='calaccess_committee_id', how='inner')

# Group by committee_name_x and sum amounts
result = joined.groupby('committee_name_x', as_index=False)['amount'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_6/target_multisource_mcts.csv", index=False)