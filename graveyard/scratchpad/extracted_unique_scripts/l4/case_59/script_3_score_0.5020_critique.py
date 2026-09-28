import pandas as pd

def clean_int_column(s):
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True), errors='coerce').fillna(0).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    # Clean integer columns
    for col in ['N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']:
        df[col] = clean_int_column(df[col].astype(str))
    dfs.append(df)

# UNION all source tables
df_all = pd.concat(dfs, ignore_index=True)

# Reorder columns to match target schema exactly
df_all = df_all[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)