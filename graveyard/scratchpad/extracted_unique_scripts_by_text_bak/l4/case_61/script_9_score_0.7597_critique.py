import pandas as pd

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

# Clean numeric columns by removing spaces, non-breaking spaces, dots, commas, but keep 'Población resto' as string (with original formatting)
def clean_numeric_str_col(col):
    return col.astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '', regex=False)

df_all['Población cabecera'] = clean_numeric_str_col(df_all['Población cabecera']).astype(int)
df_all['Población Total'] = clean_numeric_str_col(df_all['Población Total']).astype(int)
df_all['N.°'] = df_all['N.°'].astype(int)

# Keep 'Población resto' as string, but normalize spaces and non-breaking spaces to regular spaces, strip leading/trailing spaces
df_all['Población resto'] = df_all['Población resto'].astype(str).str.replace('\xa0', ' ', regex=False).str.strip()

# Convert 'Municipio' and 'Departamento' to integer if possible, else keep as string
# According to target schema, these are integers, so convert them to int
# But source examples show these are strings (names), so we must convert them to integer codes (e.g., categorical codes)
# Because target schema shows Municipio and Departamento as integer, but source has strings, we must encode them

# Encode 'Municipio' and 'Departamento' as categorical codes starting from 1 (to match target examples)
df_all['Municipio'] = df_all['Municipio'].astype('category').cat.codes + 1
df_all['Departamento'] = df_all['Departamento'].astype('category').cat.codes + 1

# Reorder columns as per target schema
df_all = df_all[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)