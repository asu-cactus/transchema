import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

# Group by conservation_status and count scientific_name occurrences
df = df0.groupby('conservation_status', dropna=False)['scientific_name'].count().reset_index()

# Rename columns to match target schema
df.columns = ['conservation_status', 'scientific_name']

# Convert scientific_name count to int (should already be int, but ensure)
df['scientific_name'] = df['scientific_name'].astype(int)

# Convert conservation_status to string (NaNs become 'nan' string, keep as is)
df['conservation_status'] = df['conservation_status'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)