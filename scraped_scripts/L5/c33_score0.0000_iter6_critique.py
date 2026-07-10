import pandas as pd
import re

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_33/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Convert GEO.id2 to string
df['GEO.id2'] = df['GEO.id2'].astype(str)

# Convert GEO.id to integer
df['GEO.id'] = pd.to_numeric(df['GEO.id'], errors='coerce').astype('Int64')

# Extract numeric part from GEO.display-label and convert to integer
def extract_numeric(label):
    if pd.isna(label):
        return pd.NA
    # Extract digits from the string
    match = re.search(r'\d+', str(label))
    if match:
        return int(match.group())
    else:
        return pd.NA

df['GEO.display-label'] = df['GEO.display-label'].apply(extract_numeric).astype('Int64')

# Convert HD01_VD01, HD02_VD01, Year to integer
df['HD01_VD01'] = pd.to_numeric(df['HD01_VD01'], errors='coerce').astype('Int64')
df['HD02_VD01'] = pd.to_numeric(df['HD02_VD01'], errors='coerce').astype('Int64')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')

# Select columns in target schema order
df = df[['GEO.id2', 'GEO.id', 'GEO.display-label', 'HD01_VD01', 'HD02_VD01', 'Year']]

# Drop rows with any NaN values to ensure data quality
df = df.dropna()

# Write to output
df.to_csv("autopipeline-benchmarks/github-pipelines/length5_33/target_multisource_mcts.csv", index=False)