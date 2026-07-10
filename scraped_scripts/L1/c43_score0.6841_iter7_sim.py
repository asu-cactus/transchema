import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# The partial plan suggests joining Source1_43_0 with itself on facid, which is redundant and will produce the same table.
# So effectively, we just use df0 as is.

# Group by fac_type and aggregate other columns by first (since facid is unique, grouping by fac_type will aggregate multiple facid)
# But target examples show facid as integer, capacity as integer, fac_name, fac_address, city_state_zip, owner, operator as integer
# However, source columns facid is string (e.g. '50R369'), so we need to convert facid to integer.
# The error in previous attempts was trying to convert '50R369' to int directly.
# So we must extract numeric part from facid string for conversion.

# Extract numeric part from facid for conversion
def extract_numeric_facid(facid):
    import re
    nums = re.findall(r'\d+', str(facid))
    return int(nums[0]) if nums else None

df0['facid'] = df0['facid'].apply(extract_numeric_facid)

# Convert capacity to integer (already integer)
df0['capacity'] = pd.to_numeric(df0['capacity'], errors='coerce').fillna(0).astype(int)

# For fac_name, fac_address, city_state_zip, owner, operator: target schema says integer, but source has strings.
# The target examples show integer values for these columns, which likely means these columns are encoded as integers (e.g. categorical codes).
# So we convert these string columns to categorical codes.

for col in ['fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']:
    df0[col] = df0[col].astype('category').cat.codes

# fac_type is string, keep as is

# Group by fac_type and facid (since facid is unique key), aggregate other columns by first
df_grouped = df0.groupby(['fac_type', 'facid'], as_index=False).agg({
    'capacity': 'first',
    'fac_name': 'first',
    'fac_address': 'first',
    'city_state_zip': 'first',
    'owner': 'first',
    'operator': 'first'
})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)