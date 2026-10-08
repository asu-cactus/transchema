import pandas as pd

def clean_number_column(s):
    # Remove all spaces (including non-breaking spaces) and convert to numeric
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True), errors='coerce')

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Clean numeric columns
df_all['Población cabecera'] = clean_number_column(df_all['Población cabecera'])
df_all['Población resto'] = clean_number_column(df_all['Población resto'])
df_all['Población Total'] = clean_number_column(df_all['Población Total'])

# Cast key columns to integer
df_all['N.°'] = df_all['N.°'].astype('Int64')

# 'Municipio' and 'Departamento' are strings in source and target examples, but target schema says integer.
# However, target examples show Municipio and Departamento as integers (probably IDs).
# Since source columns are strings, we need to convert Municipio and Departamento to integer IDs.
# But source columns are strings (names), target expects integers.
# This suggests that Municipio and Departamento columns in target are integer IDs, but source has names.
# The problem statement says all source tables must be used, but no other table provides mapping.
# Since no mapping is given, and target examples show Municipio and Departamento as integers,
# we must convert Municipio and Departamento to categorical codes (integer IDs) consistently.

# Convert Municipio and Departamento to categorical codes (integer IDs)
df_all['Municipio'] = df_all['Municipio'].astype('category').cat.codes + 1  # +1 to start IDs at 1
df_all['Departamento'] = df_all['Departamento'].astype('category').cat.codes + 1

# Cast population columns to integer
df_all['Población cabecera'] = df_all['Población cabecera'].round().astype('Int64')
df_all['Población resto'] = df_all['Población resto'].round().astype('Int64')
df_all['Población Total'] = df_all['Población Total'].round().astype('Int64')

# Format 'Población resto' as string with non-breaking space as thousands separator
df_all['Población resto'] = df_all['Población resto'].astype(str).str.replace(
    r'(\d)(?=(\d{3})+$)', r'\1\xa0', regex=True).str.strip()

# Reorder columns to match target schema
df_all = df_all[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)