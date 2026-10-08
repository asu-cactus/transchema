import pandas as pd

def clean_int_column(s):
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False), errors='coerce').astype('Int64')

src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv', index_col=0)
src2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv', index_col=0)
src3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv', index_col=0)

join_cols = ['N.°', 'Municipio', 'Departamento']
joined = pd.merge(src0, src1, on=join_cols, suffixes=('_0', '_1'))

result = pd.DataFrame()
result['Población resto'] = joined['Población resto_0'].combine_first(joined['Población resto_1'])
result['N.°'] = joined['N.°']
result['Municipio'] = joined['Municipio']
result['Departamento'] = joined['Departamento']
result['Población cabecera'] = joined['Población cabecera_0'].combine_first(joined['Población cabecera_1'])
result['Población Total'] = joined['Población Total_0'].combine_first(joined['Población Total_1'])

src2_renamed = src2.rename(columns=lambda x: x.strip())
src3_renamed = src3.rename(columns=lambda x: x.strip())

union_all = pd.concat([result, src2_renamed, src3_renamed], ignore_index=True, sort=False)

union_all['Población resto'] = union_all['Población resto'].astype(str).str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False)
union_all['Población cabecera'] = union_all['Población cabecera'].astype(str).str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False)
union_all['Población Total'] = union_all['Población Total'].astype(str).str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False)

union_all['Población resto'] = clean_int_column(union_all['Población resto'])
union_all['Población cabecera'] = clean_int_column(union_all['Población cabecera'])
union_all['Población Total'] = clean_int_column(union_all['Población Total'])

union_all['N.°'] = pd.to_numeric(union_all['N.°'], errors='coerce').astype('Int64')
union_all['Municipio'] = pd.to_numeric(union_all['Municipio'], errors='coerce').astype('Int64')
union_all['Departamento'] = pd.to_numeric(union_all['Departamento'], errors='coerce').astype('Int64')

final_cols = ['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']
final_df = union_all[final_cols]

final_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv', index=False)