import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)  # Source2_17_0
df1 = pd.read_csv(source1_path, index_col=0)  # Source2_17_1

# Join on 'state' to combine population info with broadband/federal/percent info
df_joined = pd.merge(df1, df0[['population', 'state']], on='state', how='inner')

# Group by 'state' and aggregate accordingly
agg_df = df_joined.groupby('state', as_index=False).agg(
    Federal=('Federal', 'sum'),
    Percent=('Percent', 'max'),
    Broadband_Initiative=('Broadband Initiative', 'max'),
    population=('population', 'max')
)

# Rename 'Broadband_Initiative' back to 'Broadband Initiative' to match target schema
agg_df = agg_df.rename(columns={'Broadband_Initiative': 'Broadband Initiative'})

# Reorder columns to match target schema: ['Broadband Initiative', 'Federal', 'Percent', 'state', 'population']
agg_df = agg_df[['Broadband Initiative', 'Federal', 'Percent', 'state', 'population']]

# Ensure correct dtypes
agg_df['Broadband Initiative'] = agg_df['Broadband Initiative'].astype(int)
agg_df['Federal'] = agg_df['Federal'].astype(int)
agg_df['Percent'] = agg_df['Percent'].astype(float)
agg_df['state'] = agg_df['state'].astype(str)
agg_df['population'] = agg_df['population'].astype(int)

agg_df.to_csv(target_path, index=False)