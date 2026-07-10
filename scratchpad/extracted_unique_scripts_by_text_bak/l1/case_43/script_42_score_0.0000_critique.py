import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# Convert facid and capacity to numeric
df0['facid'] = pd.to_numeric(df0['facid'], errors='coerce')
df0['capacity'] = pd.to_numeric(df0['capacity'], errors='coerce')

# Convert fac_type to string (group by)
df0['fac_type'] = df0['fac_type'].astype('string')

# Convert string columns to string type first
for col in ['fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']:
    df0[col] = df0[col].astype('string')

# Replace string columns by their lengths
for col in ['fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']:
    df0[col] = df0[col].str.len()

# Group by fac_type and facid
agg_df = df0.groupby(['fac_type', 'facid'], as_index=False).agg({
    'capacity': 'sum',
    'fac_name': 'max',
    'fac_address': 'max',
    'city_state_zip': 'max',
    'owner': 'max',
    'operator': 'max'
})

# Ensure column order matches target schema
agg_df = agg_df[['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)