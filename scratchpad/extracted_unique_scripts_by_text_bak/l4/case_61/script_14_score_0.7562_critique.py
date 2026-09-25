import pandas as pd

def clean_str_column(s):
    # Remove non-breaking spaces and normal spaces, keep as string
    if s.dtype == object:
        s = s.str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
    return s

def clean_int_column(s):
    # Remove spaces and non-breaking spaces, convert to int
    if s.dtype == object:
        s = s.str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
    return pd.to_numeric(s, errors='coerce').fillna(0).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Concatenate all sources (UNION)
df = pd.concat(dfs, ignore_index=True)

# Clean columns according to target schema:
# 'Población resto' as string cleaned of spaces
df['Población resto'] = clean_str_column(df['Población resto'])

# 'N.°' as int
df['N.°'] = clean_int_column(df['N.°'])

# 'Municipio' and 'Departamento' are strings in source, but integers in target
# Encode them as categorical codes starting from 1 to match target integer type
df['Municipio'] = df['Municipio'].astype(str)
df['Departamento'] = df['Departamento'].astype(str)

df['Municipio'] = pd.factorize(df['Municipio'])[0] + 1
df['Departamento'] = pd.factorize(df['Departamento'])[0] + 1

# 'Población cabecera' and 'Población Total' as int
df['Población cabecera'] = clean_int_column(df['Población cabecera'])
df['Población Total'] = clean_int_column(df['Población Total'])

# Reorder columns to match target schema
df = df[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)