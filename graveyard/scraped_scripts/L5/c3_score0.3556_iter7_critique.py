import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_0.csv", index_col=0)  # ['Artist', 'Albums in RS500']
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_1.csv", index_col=0)  # ['Artist', 'Top 100 Singles', 'Highest Position']
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_2.csv", index_col=0)  # ['Artist', 'Certified Units (Millions)']
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_3.csv", index_col=0)  # ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated']
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_4.csv", index_col=0)  # ['Artist', 'Influenced']
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_5.csv", index_col=0)  # ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By']

# Convert numeric columns to proper types
s1['Top 100 Singles'] = pd.to_numeric(s1['Top 100 Singles'], errors='coerce')
s1['Highest Position'] = pd.to_numeric(s1['Highest Position'], errors='coerce')
s2['Certified Units (Millions)'] = pd.to_numeric(s2['Certified Units (Millions)'], errors='coerce')
s4['Influenced'] = pd.to_numeric(s4['Influenced'], errors='coerce')
s0['Albums in RS500'] = pd.to_numeric(s0['Albums in RS500'], errors='coerce')
s5['Year Inducted'] = pd.to_numeric(s5['Year Inducted'], errors='coerce')
s5['Years Waited'] = pd.to_numeric(s5['Years Waited'], errors='coerce')
s5['# of Years Nominated'] = pd.to_numeric(s5['# of Years Nominated'], errors='coerce')

# Aggregate numeric columns in s1 by Artist (sum)
agg_s1 = s1.groupby('Artist').agg({
    'Top 100 Singles': 'sum',
    'Highest Position': 'sum'
}).reset_index()

# Aggregate s2, s4, s0 by Artist (sum)
agg_s2 = s2.groupby('Artist').agg({'Certified Units (Millions)': 'sum'}).reset_index()
agg_s4 = s4.groupby('Artist').agg({'Influenced': 'sum'}).reset_index()
agg_s0 = s0.groupby('Artist').agg({'Albums in RS500': 'sum'}).reset_index()

# Join s5 (dimension table) with aggregated s1
df = s5.merge(agg_s1, on='Artist', how='left')

# Join with aggregated s2
df = df.merge(agg_s2, on='Artist', how='left')

# Join with aggregated s4
df = df.merge(agg_s4, on='Artist', how='left')

# Join with aggregated s0
df = df.merge(agg_s0, on='Artist', how='left')

# Ensure columns are in target schema order
result = df[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By',
             'Influenced', 'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position']]

# Convert types to match target schema
result['Year Inducted'] = pd.to_numeric(result['Year Inducted'], errors='coerce')
result['Years Waited'] = pd.to_numeric(result['Years Waited'], errors='coerce').astype('Int64')
result['# of Years Nominated'] = pd.to_numeric(result['# of Years Nominated'], errors='coerce').astype('Int64')
result['Influenced'] = pd.to_numeric(result['Influenced'], errors='coerce').astype('Int64')
result['Albums in RS500'] = pd.to_numeric(result['Albums in RS500'], errors='coerce').astype('Int64')
result['Top 100 Singles'] = pd.to_numeric(result['Top 100 Singles'], errors='coerce').astype('Int64')
result['Highest Position'] = pd.to_numeric(result['Highest Position'], errors='coerce').astype('Int64')
result['Certified Units (Millions)'] = pd.to_numeric(result['Certified Units (Millions)'], errors='coerce')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_3/target_multisource_mcts.csv", index=False)