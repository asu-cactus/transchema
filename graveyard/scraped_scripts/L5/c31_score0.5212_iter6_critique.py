import pandas as pd
import re

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_31/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Extract integer from 'GEO.display-label' which looks like "ZCTA5 91932"
# We take the numeric part after the space
df['GEO.display-label'] = df['GEO.display-label'].astype(str).str.extract(r'(\d+)$')[0]

# Convert columns to correct types matching target schema
df['GEO.id'] = df['GEO.id'].astype(str)
df['GEO.id2'] = pd.to_numeric(df['GEO.id2'], errors='coerce').astype('Int64')
df['GEO.display-label'] = pd.to_numeric(df['GEO.display-label'], errors='coerce').astype('Int64')
df['HD01_VD01'] = pd.to_numeric(df['HD01_VD01'], errors='coerce').astype('Int64')
df['HD02_VD01'] = pd.to_numeric(df['HD02_VD01'], errors='coerce').astype('Int64')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')

# Remove duplicates if any (to match target unique keys)
df = df.drop_duplicates(subset=['GEO.id', 'GEO.id2', 'GEO.display-label', 'HD01_VD01', 'HD02_VD01', 'Year'])

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_31/target_multisource_mcts.csv", index=False)