import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_3.csv", index_col=0)

# UNION Source5_4_0 and Source5_4_2
union_0_2 = pd.concat([s0, s2], ignore_index=True, sort=False)

# JOIN union with Source5_4_1 on Artist
merged_0_1 = pd.merge(union_0_2, s1, on="Artist", how="left")

# JOIN above with Source5_4_3 on Artist
merged_all = pd.merge(merged_0_1, s3, on="Artist", how="left")

# Convert numeric columns to appropriate types before aggregation
merged_all['Year Inducted'] = pd.to_numeric(merged_all['Year Inducted'], errors='coerce')
merged_all['Years Waited'] = pd.to_numeric(merged_all['Years Waited'], errors='coerce')
merged_all['# of Years Nominated'] = pd.to_numeric(merged_all['# of Years Nominated'], errors='coerce')
merged_all['Influenced'] = pd.to_numeric(merged_all['Influenced'], errors='coerce')
merged_all['Certified Units (Millions)'] = pd.to_numeric(merged_all['Certified Units (Millions)'], errors='coerce')

# Define aggregation functions
agg_dict = {
    'Year Inducted': 'mean',
    'Years Waited': 'mean',
    '# of Years Nominated': 'mean',
    'Inducted By': 'first',
    'Influenced': 'sum',
    'Certified Units (Millions)': 'sum'
}

grouped = merged_all.groupby('Artist', as_index=False).agg(agg_dict)

# Convert types to match target schema
grouped['Year Inducted'] = grouped['Year Inducted'].astype(float)
grouped['Years Waited'] = grouped['Years Waited'].round().astype('Int64')
grouped['# of Years Nominated'] = grouped['# of Years Nominated'].round().astype('Int64')
grouped['Influenced'] = grouped['Influenced'].astype('Int64')
grouped['Certified Units (Millions)'] = grouped['Certified Units (Millions)'].astype(float)

# Reorder columns to match target schema
final = grouped[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced', 'Certified Units (Millions)']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_4/target_multisource_mcts.csv", index=False)