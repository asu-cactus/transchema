import pandas as pd

def clean_int_column(s):
    # Remove spaces and non-breaking spaces, convert to int
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False), errors='coerce').fillna(0).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['Población cabecera'] = clean_int_column(df['Población cabecera'])
df['Población resto'] = clean_int_column(df['Población resto'])
df['Población Total'] = clean_int_column(df['Población Total'])
df['N.°'] = pd.to_numeric(df['N.°'], errors='coerce').fillna(0).astype(int)

# Convert Departamento string to integer codes to match target schema
df['Departamento'] = pd.factorize(df['Departamento'])[0] + 1  # +1 to avoid zero if needed

df = df[['Municipio', 'N.°', 'Departamento', 'Población cabecera', 'Población resto', 'Población Total']]

# Group by Municipio, N.°, Departamento and sum population columns
df = df.groupby(['Municipio', 'N.°', 'Departamento'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_60/target_multisource_mcts.csv", index=False)