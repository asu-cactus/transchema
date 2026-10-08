import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# Ensure correct types
df['fac_type'] = df['fac_type'].astype(str)
df['facid'] = pd.to_numeric(df['facid'], errors='coerce')
df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce')
df['fac_name'] = df['fac_name'].astype(str)
df['fac_address'] = df['fac_address'].astype(str)
df['city_state_zip'] = df['city_state_zip'].astype(str)
df['owner'] = df['owner'].astype(str)
df['operator'] = df['operator'].astype(str)

# Group by fac_type and count each other column
grouped = df.groupby('fac_type').agg({
    'facid': 'count',
    'capacity': 'count',
    'fac_name': 'count',
    'fac_address': 'count',
    'city_state_zip': 'count',
    'owner': 'count',
    'operator': 'count'
}).reset_index()

# Rename columns to match target schema exactly
grouped = grouped[['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)