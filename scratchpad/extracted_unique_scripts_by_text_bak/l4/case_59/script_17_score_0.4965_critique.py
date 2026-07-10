import pandas as pd

def clean_int_column(s):
    # Remove spaces and non-breaking spaces, convert to int
    return pd.to_numeric(s.astype(str).str.replace(r'\s+', '', regex=True).str.replace(' ', '', regex=False), errors='coerce').fillna(0).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    # Clean numeric columns
    for col in ['N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']:
        df[col] = clean_int_column(df[col])
    dfs.append(df)

# UNION all source tables
union_df = pd.concat(dfs, ignore_index=True)

# GROUP BY key columns and sum population columns
grouped = union_df.groupby(['Departamento', 'N.°', 'Municipio'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

# Reorder columns to match target schema exactly
grouped = grouped[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)