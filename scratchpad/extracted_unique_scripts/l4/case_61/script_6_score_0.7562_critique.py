import pandas as pd

def clean_numeric_str_column(s):
    # Remove non-breaking spaces and spaces, then convert to int
    return pd.to_numeric(s.astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False), errors='coerce').astype('Int64')

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Clean 'Población resto' as string, remove spaces and non-breaking spaces but keep as string
df['Población resto'] = df['Población resto'].astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)

# Clean numeric columns
df['N.°'] = clean_numeric_str_column(df['N.°'])

# Municipio and Departamento are strings in source but integers in target, so factorize them to get integer IDs
df['Municipio'] = pd.factorize(df['Municipio'])[0] + 1  # +1 to start IDs at 1
df['Departamento'] = pd.factorize(df['Departamento'])[0] + 1

df['Población cabecera'] = clean_numeric_str_column(df['Población cabecera'])
df['Población Total'] = clean_numeric_str_column(df['Población Total'])

# Group by keys to remove duplicates and aggregate sums for population columns
df = df.groupby(['Población resto', 'N.°', 'Municipio', 'Departamento'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población Total': 'sum'
})

# Reorder columns to match target schema
df = df[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)