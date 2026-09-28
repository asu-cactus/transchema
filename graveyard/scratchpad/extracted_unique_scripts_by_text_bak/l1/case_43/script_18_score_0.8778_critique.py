import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# Group by fac_type
df_grouped = df.groupby('fac_type', as_index=False).agg({
    'facid': pd.Series.nunique,          # count distinct facid
    'capacity': 'sum',                   # sum capacity
    'fac_name': pd.Series.nunique,      # count distinct fac_name
    'fac_address': pd.Series.nunique,   # count distinct fac_address
    'city_state_zip': pd.Series.nunique,# count distinct city_state_zip
    'owner': pd.Series.nunique,         # count distinct owner
    'operator': pd.Series.nunique       # count distinct operator
})

# Rename columns to match target schema exactly (already matched)
# Convert all columns except fac_type to int (nunique and sum produce int or float)
for col in ['facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']:
    df_grouped[col] = df_grouped[col].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)