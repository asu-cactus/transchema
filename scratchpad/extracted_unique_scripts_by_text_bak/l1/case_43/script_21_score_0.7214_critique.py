import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# Group by fac_type and count distinct values for other columns
df_grouped = df0.groupby('fac_type', dropna=False).agg({
    'facid': pd.Series.nunique,
    'capacity': pd.Series.nunique,
    'fac_name': pd.Series.nunique,
    'fac_address': pd.Series.nunique,
    'city_state_zip': pd.Series.nunique,
    'owner': pd.Series.nunique,
    'operator': pd.Series.nunique
}).reset_index()

# Rename columns to match target schema exactly (already matched)
# Ensure types: fac_type string, others integer
df_grouped['fac_type'] = df_grouped['fac_type'].astype(str)
for col in ['facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']:
    df_grouped[col] = df_grouped[col].astype('Int64')

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)