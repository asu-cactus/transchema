import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# Factorize string columns to integer codes
for col in ['fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']:
    df0[col], _ = pd.factorize(df0[col])

# Group by fac_type
agg = df0.groupby('fac_type', as_index=False).agg({
    'facid': 'count',       # count of facid per fac_type
    'capacity': 'sum',      # sum capacity per fac_type
    'fac_name': 'min',      # min of factorized fac_name
    'fac_address': 'min',   # min of factorized fac_address
    'city_state_zip': 'min',# min of factorized city_state_zip
    'owner': 'min',         # min of factorized owner
    'operator': 'min'       # min of factorized operator
})

# Rename columns to match target schema
agg = agg.rename(columns={'facid': 'facid'})

# Ensure correct column order as per target schema
agg = agg[['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']]

# Convert facid and capacity to int (already int), others are int from factorization
agg['facid'] = agg['facid'].astype(int)
agg['capacity'] = agg['capacity'].astype(int)
agg['fac_name'] = agg['fac_name'].astype(int)
agg['fac_address'] = agg['fac_address'].astype(int)
agg['city_state_zip'] = agg['city_state_zip'].astype(int)
agg['owner'] = agg['owner'].astype(int)
agg['operator'] = agg['operator'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)