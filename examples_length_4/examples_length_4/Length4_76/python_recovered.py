import pandas as pd

# File paths
source0_path = 'autopipeline-benchmarks/github-pipelines/length4_76/test_0.csv'
source1_path = 'autopipeline-benchmarks/github-pipelines/length4_76/test_1.csv'
source2_path = 'autopipeline-benchmarks/github-pipelines/length4_76/test_2.csv'
target_path = 'autopipeline-benchmarks/github-pipelines/length4_76/target_multisource_cot.csv'

# Load source tables, ignoring first index column as per instructions
source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)
source2 = pd.read_csv(source2_path, index_col=0)

# Rename Source0.Description to Description_x for clarity
source0 = source0.rename(columns={'Description': 'Description_x'})

# Rename Source1.Description to Description_y
source1 = source1.rename(columns={'Description': 'Description_y'})

# Join Source0 and Source1 on 'Code'
df_01 = pd.merge(source0[['Rank', 'Code', 'Description_x']], 
                 source1[['Code', 'Description_y']], 
                 on='Code', 
                 how='inner')

# From Source2, collect all unique airport IDs from ORIGIN_AIRPORT_ID and DEST_AIRPORT_ID,
# which may correspond to 'Code' in targets
airport_ids = pd.unique(
    pd.concat([source2['ORIGIN_AIRPORT_ID'], source2['DEST_AIRPORT_ID']])
)

# Filter df_01 to keep only rows where 'Code' exists in airport_ids from Source2
df_filtered = df_01[df_01['Code'].isin(airport_ids)].copy()

# Reset index for clean output
df_filtered.reset_index(drop=True, inplace=True)

# Ensure correct datatypes match target schema:
df_filtered['Code'] = df_filtered['Code'].astype(int)
df_filtered['Rank'] = df_filtered['Rank'].astype(int)
df_filtered['Description_x'] = df_filtered['Description_x'].astype(str)
df_filtered['Description_y'] = df_filtered['Description_y'].astype(str)

# Write to csv without index
df_filtered.to_csv(target_path, index=False)