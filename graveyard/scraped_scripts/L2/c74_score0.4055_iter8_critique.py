import pandas as pd
import re

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_74/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_74/training_1.csv", index_col=0)

# Join on Mouse ID (inner join to avoid NaNs)
merged = pd.merge(df0, df1, on='Mouse ID', how='inner')

# Convert Mouse ID string to integer by extracting digits
def extract_int_id(s):
    m = re.search(r'\d+', s)
    return int(m.group()) if m else None

merged['Mouse ID'] = merged['Mouse ID'].map(extract_int_id)

# Drop rows where conversion failed (None)
merged = merged.dropna(subset=['Mouse ID'])

# Convert Mouse ID to int type
merged['Mouse ID'] = merged['Mouse ID'].astype(int)

# Group by Drug, Timepoint, Mouse ID to get unique rows (no aggregation needed)
result = merged[['Drug', 'Timepoint', 'Mouse ID']].drop_duplicates()

# Sort by Drug, Timepoint, Mouse ID to have consistent output (optional)
result = result.sort_values(by=['Drug', 'Timepoint', 'Mouse ID']).reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_74/target_multisource_mcts.csv", index=False)