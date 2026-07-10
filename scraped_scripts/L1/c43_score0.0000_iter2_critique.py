import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

df = df0.copy()

# Convert facid and capacity to numeric
df['facid'] = pd.to_numeric(df['facid'], errors='coerce')
df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce')

# Convert fac_type to string
df['fac_type'] = df['fac_type'].astype(str)

# Convert string columns to their lengths
for col in ['fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']:
    df[col] = df[col].astype(str).apply(len)

# Group by fac_type and facid, aggregate sums for other columns
agg_df = df.groupby(['fac_type', 'facid'], as_index=False).agg({
    'capacity': 'sum',
    'fac_name': 'sum',
    'fac_address': 'sum',
    'city_state_zip': 'sum',
    'owner': 'sum',
    'operator': 'sum'
})

# Reorder columns to match target schema
agg_df = agg_df[['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)