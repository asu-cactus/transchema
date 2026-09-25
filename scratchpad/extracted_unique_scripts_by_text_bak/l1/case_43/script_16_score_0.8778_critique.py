import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# Group by 'fac_type' and count non-null values in other columns
agg_df = df0.groupby('fac_type').agg({
    'facid': 'count',
    'capacity': 'count',
    'fac_name': 'count',
    'fac_address': 'count',
    'city_state_zip': 'count',
    'owner': 'count',
    'operator': 'count'
}).reset_index()

# Rename columns to match target schema exactly
agg_df.columns = ['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']

# Convert all columns except 'fac_type' to integer type
for col in agg_df.columns:
    if col != 'fac_type':
        agg_df[col] = agg_df[col].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)