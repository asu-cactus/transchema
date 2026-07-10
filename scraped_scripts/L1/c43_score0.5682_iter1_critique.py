import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# fac_type is string, keep as is
df0['fac_type'] = df0['fac_type'].astype(str)

# Convert numeric columns to numeric, coercing errors to NaN, then fill NaN with 0 and convert to int
for col in ['facid', 'capacity']:
    df0[col] = pd.to_numeric(df0[col], errors='coerce').fillna(0).astype(int)

# The other columns are textual but target expects integers, so aggregate counts or sums
# We will treat them as counts of non-null entries per fac_type
# But since target examples show sums, we convert textual columns to counts of non-null entries per group

# Create indicator columns for counting non-null entries
for col in ['fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']:
    df0[col] = df0[col].notnull().astype(int)

# Group by fac_type and aggregate sums
agg_df = df0.groupby('fac_type').agg({
    'facid': 'sum',
    'capacity': 'sum',
    'fac_name': 'sum',
    'fac_address': 'sum',
    'city_state_zip': 'sum',
    'owner': 'sum',
    'operator': 'sum'
}).reset_index()

# Ensure columns order matches target schema
agg_df = agg_df[['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)