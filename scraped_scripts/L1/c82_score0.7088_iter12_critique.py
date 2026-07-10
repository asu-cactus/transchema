import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

# Convert scientific_name to numeric integer type (coerce errors to NaN)
df0['scientific_name'] = pd.to_numeric(df0['scientific_name'], errors='coerce').astype('Int64')

# conservation_status as string type
df0['conservation_status'] = df0['conservation_status'].astype('string')

# Group by conservation_status and count scientific_name
df = df0.groupby('conservation_status', dropna=False).agg({'scientific_name': 'count'}).reset_index()

# Rename columns to match target schema exactly
df.columns = ['conservation_status', 'scientific_name']

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)