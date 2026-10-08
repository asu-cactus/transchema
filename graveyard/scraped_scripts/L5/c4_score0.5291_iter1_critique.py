import pandas as pd
import numpy as np

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_3.csv", index_col=0)

# Convert numeric columns with coercion
source0['Year Inducted'] = pd.to_numeric(source0['Year Inducted'], errors='coerce')
source2['Year Inducted'] = pd.to_numeric(source2['Year Inducted'], errors='coerce')

source0['Years Waited'] = pd.to_numeric(source0['Years Waited'], errors='coerce').astype('Int64')
source2['Years Waited'] = pd.to_numeric(source2['Years Waited'], errors='coerce').astype('Int64')

source0['# of Years Nominated'] = pd.to_numeric(source0['# of Years Nominated'], errors='coerce').astype('Int64')
source2['# of Years Nominated'] = pd.to_numeric(source2['# of Years Nominated'], errors='coerce').astype('Int64')

source1['Influenced'] = pd.to_numeric(source1['Influenced'], errors='coerce').astype('Int64')

source3['Certified Units (Millions)'] = pd.to_numeric(source3['Certified Units (Millions)'], errors='coerce')

# Join source0 and source2 on Artist (outer join to keep all info)
joined_0_2 = pd.merge(source0, source2, on='Artist', how='outer', suffixes=('_0', '_2'))

# For columns present in both, combine them by taking the first non-null value (prefer source0 if available)
def coalesce(col0, col2):
    return col0.combine_first(col2)

joined_0_2['Year Inducted'] = coalesce(joined_0_2['Year Inducted_0'], joined_0_2['Year Inducted_2'])
joined_0_2['Years Waited'] = coalesce(joined_0_2['Years Waited_0'], joined_0_2['Years Waited_2'])
joined_0_2['# of Years Nominated'] = coalesce(joined_0_2['# of Years Nominated_0'], joined_0_2['# of Years Nominated_2'])
joined_0_2['Inducted By'] = joined_0_2['Inducted By']  # only in source0

# Keep only needed columns after coalescing
joined_0_2 = joined_0_2[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By']]

# Join with source1 (Influenced)
joined_0_2_1 = pd.merge(joined_0_2, source1, on='Artist', how='left')

# Join with source3 (Certified Units)
final_join = pd.merge(joined_0_2_1, source3, on='Artist', how='left')

# Group by Artist and aggregate
# For numeric columns: mean
# For 'Inducted By' (string), take first non-null value per group

def first_non_null(series):
    return series.dropna().iloc[0] if not series.dropna().empty else np.nan

agg_dict = {
    'Year Inducted': 'mean',
    'Years Waited': 'mean',
    '# of Years Nominated': 'mean',
    'Inducted By': first_non_null,
    'Influenced': 'mean',
    'Certified Units (Millions)': 'mean'
}

grouped = final_join.groupby('Artist', as_index=False).agg(agg_dict)

# Cast types to match target schema
grouped['Year Inducted'] = grouped['Year Inducted'].astype(float)
grouped['Years Waited'] = grouped['Years Waited'].round().astype('Int64')
grouped['# of Years Nominated'] = grouped['# of Years Nominated'].round().astype('Int64')
grouped['Influenced'] = grouped['Influenced'].round().astype('Int64')
grouped['Certified Units (Millions)'] = grouped['Certified Units (Millions)'].astype(float)
grouped['Inducted By'] = grouped['Inducted By'].astype('string')

# Reorder columns exactly as target schema
final = grouped[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced', 'Certified Units (Millions)']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_4/target_multisource_mcts.csv", index=False)