import pandas as pd

def clean_number_column(col):
    # Remove non-breaking spaces and spaces, keep as string for 'Población resto'
    return col.str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Clean 'Población resto' as string (remove spaces but keep as string)
df['Población resto'] = clean_number_column(df['Población resto'])

# Clean and convert other population columns to int
df['Población cabecera'] = clean_number_column(df['Población cabecera']).astype(int)
df['Población Total'] = clean_number_column(df['Población Total']).astype(int)

# Convert 'N.°' to int
df['N.°'] = df['N.°'].astype(int)

# Encode 'Municipio' and 'Departamento' as integers (label encoding)
df['Municipio'] = pd.factorize(df['Municipio'])[0] + 1  # +1 to start codes at 1
df['Departamento'] = pd.factorize(df['Departamento'])[0] + 1

# Group by 'N.°' and aggregate other columns by first (assuming unique per N.°)
df = df.groupby('N.°', as_index=False).agg({
    'Población resto': 'first',
    'Municipio': 'first',
    'Departamento': 'first',
    'Población cabecera': 'first',
    'Población Total': 'first'
})

# Reorder columns to match target schema
df = df[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)