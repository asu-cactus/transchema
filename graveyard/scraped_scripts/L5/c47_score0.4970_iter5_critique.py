import pandas as pd
import numpy as np

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_47/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_4.csv"
]

# Read all sources
df0 = pd.read_csv(paths[0], index_col=0)
df1 = pd.read_csv(paths[1], index_col=0)
df2 = pd.read_csv(paths[2], index_col=0)
df3 = pd.read_csv(paths[3], index_col=0)
df4 = pd.read_csv(paths[4], index_col=0)

# Join all sources on WarID (inner join to keep only wars present in all sources)
df = df0.merge(df1, on='WarID', suffixes=('_0', '_1'))
df = df.merge(df2, on='WarID', suffixes=('', '_2'))
df = df.merge(df3, on='WarID', suffixes=('', '_3'))
df = df.merge(df4, on='WarID', suffixes=('', '_4'))

# After join, columns are duplicated with suffixes, e.g. PolityName_0, PolityName_1, PolityName_2, etc.
# We need to consolidate columns by choosing one non-null value per attribute from the sources.

def coalesce_columns(df, base_col):
    # Collect all columns with base_col in their name
    cols = [c for c in df.columns if c == base_col or c.startswith(base_col + '_')]
    # Coalesce by taking first non-null value row-wise
    return df[cols].bfill(axis=1).iloc[:, 0]

# Columns to coalesce (all columns except WarID)
cols_to_coalesce = ['PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Outcome', 'Deaths']

df_out = pd.DataFrame()
df_out['WarID'] = df['WarID']

for col in cols_to_coalesce:
    df_out[col] = coalesce_columns(df, col)

# Convert PolityName and Initiator to string first (some may be NaN)
df_out['PolityName'] = df_out['PolityName'].astype(str)
df_out['Initiator'] = df_out['Initiator'].astype(str)

# Convert PolityName and Initiator to categorical codes starting from 1
df_out['PolityName'] = pd.Categorical(df_out['PolityName']).codes + 1
df_out['Initiator'] = pd.Categorical(df_out['Initiator']).codes + 1

# Convert numeric columns to integers, filling NaN with 0
for col in ['Outcome', 'WarID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Deaths']:
    df_out[col] = pd.to_numeric(df_out[col], errors='coerce').fillna(0).astype(int)

# Reorder columns to target schema order
df_out = df_out[['Outcome', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Deaths']]

# Write output
df_out.to_csv("autopipeline-benchmarks/github-pipelines/length5_47/target_multisource_mcts.csv", index=False)