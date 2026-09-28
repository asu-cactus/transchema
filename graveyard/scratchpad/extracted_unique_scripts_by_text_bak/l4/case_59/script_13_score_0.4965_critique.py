import pandas as pd

def clean_int_column(s):
    # Remove spaces and non-breaking spaces, convert to int, fill NaN with 0
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False), errors='coerce').fillna(0).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

for df in dfs:
    df['N.°'] = clean_int_column(df['N.°'].astype(str))
    # Municipio is string in source but target expects integer, so convert Municipio to int if possible
    # However, Municipio in source is string (city names), but target schema says Municipio is integer.
    # This is suspicious: target schema says Municipio is integer, but source Municipio is string (city names).
    # The target examples show Municipio as integer (e.g., 1, 81, 5), but source Municipio is string (e.g., 'Uribia', 'Maicao').
    # This suggests Municipio in target is an integer code, not the name.
    # So we must convert Municipio string to some integer code.
    # Since no mapping is given, we can assign a unique integer code per Municipio string.
    # To do this consistently across all dfs, we must concatenate first, then assign codes.
    # So here, keep Municipio as string for now.
    df['Población cabecera'] = clean_int_column(df['Población cabecera'].astype(str))
    df['Población resto'] = clean_int_column(df['Población resto'].astype(str))
    df['Población Total'] = clean_int_column(df['Población Total'].astype(str))
    df['Departamento'] = df['Departamento'].astype(str)

union_df = pd.concat(dfs, ignore_index=True)

# Now convert Municipio strings to integer codes consistently
union_df['Municipio'] = union_df['Municipio'].astype('category').cat.codes + 1  # +1 to start codes at 1

# Group by Departamento, N.°, Municipio and sum population columns
grouped = union_df.groupby(['Departamento', 'N.°', 'Municipio'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

# Reorder columns to match target schema exactly
grouped = grouped[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)