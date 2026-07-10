import pandas as pd
import re

# Read source tables
df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_20/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_20/training_1.csv', index_col=0)

# Join on Mouse ID (string)
df = pd.merge(df0, df1, on='Mouse ID')

# Extract integer Mouse ID from string
df['Mouse ID'] = df['Mouse ID'].apply(lambda x: int(re.sub(r'\D', '', x)) if pd.notnull(x) else x)

# Ensure types
df['Timepoint'] = df['Timepoint'].astype(int)
df['Drug'] = df['Drug'].astype(str)

# Group by Drug and Timepoint, aggregate count distinct Mouse ID
result = df.groupby(['Drug', 'Timepoint'], as_index=False).agg({'Mouse ID': pd.Series.nunique})

# Write output with exact target schema and column order
result.to_csv('autopipeline-benchmarks/github-pipelines/length2_20/target_multisource_mcts.csv', index=False)