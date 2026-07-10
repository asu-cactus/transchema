import pandas as pd

def clean_int_column(s):
    # Remove all whitespace including non-breaking spaces, then convert to int
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False), errors='coerce').fillna(0).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Clean integer columns properly
df['N.°'] = clean_int_column(df['N.°'].astype(str))
# 'Municipio' is string in source but integer in target, so convert similarly
df['Municipio'] = clean_int_column(df['Municipio'].astype(str))
df['Población cabecera'] = clean_int_column(df['Población cabecera'].astype(str))
df['Población resto'] = clean_int_column(df['Población resto'].astype(str))
df['Población Total'] = clean_int_column(df['Población Total'].astype(str))

# Reorder columns to match target schema exactly
df = df[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)