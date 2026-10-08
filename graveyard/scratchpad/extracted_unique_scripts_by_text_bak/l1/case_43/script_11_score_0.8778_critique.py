import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# Group by fac_type
agg = df0.groupby("fac_type").agg({
    "facid": pd.Series.nunique,       # count distinct facid
    "capacity": "sum",                # sum capacity
    "fac_name": "count",              # count non-null fac_name
    "fac_address": "count",           # count non-null fac_address
    "city_state_zip": "count",        # count non-null city_state_zip
    "owner": "count",                 # count non-null owner
    "operator": "count"               # count non-null operator
}).reset_index()

# Rename columns to match target schema exactly
agg.columns = ['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']

# Ensure integer types for all columns except fac_type
for col in agg.columns:
    if col != 'fac_type':
        agg[col] = agg[col].astype(int)

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)