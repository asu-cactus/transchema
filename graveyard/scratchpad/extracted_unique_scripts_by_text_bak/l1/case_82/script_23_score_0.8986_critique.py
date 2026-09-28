import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

# Filter rows where conservation_status is not null or empty
df_filtered = df0[(df0['conservation_status'].notna()) & (df0['conservation_status'] != '')]

# Convert scientific_name to string to count distinct values correctly
# (scientific_name is string in source, target expects integer count)
# Group by conservation_status and count distinct scientific_name
result = df_filtered.groupby('conservation_status', as_index=False)['scientific_name'].nunique()

# Rename columns to match target schema
result.columns = ['conservation_status', 'scientific_name']

# scientific_name column is count, so integer type
result['scientific_name'] = result['scientific_name'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)