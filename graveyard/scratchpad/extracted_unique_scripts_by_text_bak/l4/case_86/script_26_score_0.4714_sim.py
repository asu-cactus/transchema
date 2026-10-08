import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_4.csv", index_col=0)

join_0_1 = pd.merge(df0, df1, on="titulo", suffixes=('_0', '_1'))
join_0_1_3 = pd.merge(join_0_1, df3, left_on="titulo", right_on="titulo", suffixes=('', '_3'))
join_0_1_3_4 = pd.merge(join_0_1_3, df4, left_on="titulo", right_on="titulo", suffixes=('', '_4'))

# Select columns from the last join that correspond to the target schema
# Columns from df4 have priority, then df3, then df1, then df0 (due to suffixes)
# We pick columns from df4 if present, else from df3, else from df1, else from df0

def coalesce_columns(row, col_base):
    for suffix in ['', '_4', '_3', '_1', '_0']:
        col = col_base + suffix
        if col in row and pd.notna(row[col]):
            return row[col]
    return None

cols = ['titulo', 'tipo', 'precio', 'condicion', 'ubicacion', 'tiempo', 'reputacion', 'pago']
df_joined = pd.DataFrame()
for col in cols:
    # Try to get the column from df4 first, then df3, then df1, then df0
    # Because merge suffixes put df4 columns without suffix, df3 with _3, df1 with _1, df0 with _0
    if col in join_0_1_3_4.columns:
        df_joined[col] = join_0_1_3_4[col]
    elif col + '_4' in join_0_1_3_4.columns:
        df_joined[col] = join_0_1_3_4[col + '_4']
    elif col + '_3' in join_0_1_3_4.columns:
        df_joined[col] = join_0_1_3_4[col + '_3']
    elif col + '_1' in join_0_1_3_4.columns:
        df_joined[col] = join_0_1_3_4[col + '_1']
    elif col + '_0' in join_0_1_3_4.columns:
        df_joined[col] = join_0_1_3_4[col + '_0']
    else:
        df_joined[col] = pd.NA

# Now union with df2 (which has the same schema as target)
df_final = pd.concat([df_joined, df2], ignore_index=True, sort=False)

# Ensure correct dtypes
df_final['titulo'] = df_final['titulo'].astype(str)
df_final['tipo'] = df_final['tipo'].astype(str)
df_final['precio'] = pd.to_numeric(df_final['precio'], errors='coerce')
df_final['condicion'] = df_final['condicion'].astype(str)
df_final['ubicacion'] = df_final['ubicacion'].astype(str)
df_final['tiempo'] = df_final['tiempo'].astype(str)
df_final['reputacion'] = df_final['reputacion'].astype(str)
df_final['pago'] = df_final['pago'].astype(str)

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts.csv", index=False)