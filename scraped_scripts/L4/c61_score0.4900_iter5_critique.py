import pandas as pd

def clean_int_column(s):
    # Remove spaces and non-breaking spaces, then convert to integer
    return pd.to_numeric(s.astype(str).str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False), errors='coerce').astype('Int64')

# Read all sources
src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv', index_col=0)
src2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv', index_col=0)
src3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv', index_col=0)

# Concatenate all sources (UNION)
union_all = pd.concat([src0, src1, src2, src3], ignore_index=True, sort=False)

# Clean and convert population columns to integers
union_all['Población resto'] = clean_int_column(union_all['Población resto'])
union_all['Población cabecera'] = clean_int_column(union_all['Población cabecera'])
union_all['Población Total'] = clean_int_column(union_all['Población Total'])

# Convert key columns to integers
union_all['N.°'] = pd.to_numeric(union_all['N.°'], errors='coerce').astype('Int64')
union_all['Municipio'] = pd.to_numeric(union_all['Municipio'], errors='coerce').astype('Int64')
union_all['Departamento'] = pd.to_numeric(union_all['Departamento'], errors='coerce').astype('Int64')

# Group by key columns and sum population columns
final_df = union_all.groupby(['N.°', 'Municipio', 'Departamento'], dropna=False, as_index=False).agg({
    'Población resto': 'sum',
    'Población cabecera': 'sum',
    'Población Total': 'sum'
})

# Reorder columns to match target schema: ['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']
final_df = final_df[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

# Write output
final_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv', index=False)