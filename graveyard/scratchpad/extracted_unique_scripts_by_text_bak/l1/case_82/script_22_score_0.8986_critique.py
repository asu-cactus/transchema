import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

# Drop rows with missing conservation_status as target examples do not include NaN conservation_status
df0 = df0.dropna(subset=['conservation_status'])

# Normalize scientific_name by stripping whitespace and converting to consistent case
df0['scientific_name'] = df0['scientific_name'].str.strip()

# Group by conservation_status and count distinct scientific_name
result = df0.groupby('conservation_status')['scientific_name'].nunique().reset_index()

# Rename columns to match target schema
result.columns = ['conservation_status', 'scientific_name']

# Convert count to int
result['scientific_name'] = result['scientific_name'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)