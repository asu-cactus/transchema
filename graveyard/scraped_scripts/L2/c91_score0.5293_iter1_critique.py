import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_91/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_91/training_1.csv", index_col=0)

# Join on calaccess_committee_id
df_joined = pd.merge(df0, df1[['calaccess_committee_id', 'committee_name']], on='calaccess_committee_id', how='inner')

# Rename committee_name from Source1 to committee_name_x to match target schema
df_joined = df_joined.rename(columns={'committee_name': 'committee_name_x'})

# Group by committee_name_x and sum amount
agg_df = df_joined.groupby('committee_name_x', as_index=False)['amount'].sum()

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_91/target_multisource_mcts.csv", index=False)