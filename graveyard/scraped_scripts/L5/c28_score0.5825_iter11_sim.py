import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_1.csv", index_col=0)

# Prepare df0 for union: add CP column with NaN, keep columns: CodProvincia, CodMunicipio, CP, Municipio, Poblacion, Provincia
df0_union = df0.copy()
df0_union['CP'] = pd.NA
df0_union = df0_union[['CodProvincia', 'CodMunicipio', 'CP', 'Municipio', 'Poblacion', 'Provincia']]

# Prepare df1 for union: add Poblacion and Provincia columns with NaN, keep columns: CodProvincia, CodMunicipio, CP, Municipio, Poblacion, Provincia
df1_union = df1.copy()
df1_union['Poblacion'] = pd.NA
df1_union['Provincia'] = pd.NA
df1_union = df1_union[['CodProvincia', 'CodMunicipio', 'CP', 'Municipio', 'Poblacion', 'Provincia']]

# Union the two dataframes
df_union = pd.concat([df0_union, df1_union], ignore_index=True)

# Now, to produce the target schema: ['CP': int, 'Municipio': int, 'SumPoblacion': int, 'Provincia': string]
# We have CP (int, from df1 or NaN), Municipio (string in sources, but target expects int), SumPoblacion (sum of Poblacion), Provincia (string)

# Municipio in target is integer, but in sources it's string. However, in source 0 Municipio is string, in source 1 Municipio is string.
# But target example shows Municipio as integer. Looking at source schemas:
# Source0: Municipio is string, CodMunicipio is int
# Source1: Municipio is string, CodMunicipio is int
# Target schema Municipio is int, so likely Municipio in target corresponds to CodMunicipio in sources.

# CP is int, from source1 only, NaN in source0 rows
# SumPoblacion is sum of Poblacion grouped by CP, Municipio, Provincia
# Provincia is string, from source0 or source1 (source1 has NaN Provincia)

# So we need to fill Provincia for rows from source1 by joining with source0 on CodProvincia, CodMunicipio, Municipio

# First, fill Provincia in df1 by joining with df0 on CodProvincia, CodMunicipio, Municipio
df1_prov = df1.copy()
df0_prov = df0[['CodProvincia', 'CodMunicipio', 'Municipio', 'Provincia']].drop_duplicates()
df1_prov = df1_prov.merge(df0_prov, on=['CodProvincia', 'CodMunicipio', 'Municipio'], how='left')

# Now combine df0 and df1_prov with consistent columns for aggregation
df0_agg = df0[['CodProvincia', 'CodMunicipio', 'Municipio', 'Provincia', 'Poblacion']].copy()
df0_agg['CP'] = pd.NA
df1_agg = df1_prov[['CodProvincia', 'CodMunicipio', 'Municipio', 'Provincia', 'CP']].copy()
df1_agg['Poblacion'] = 0

# Concatenate for aggregation
df_all = pd.concat([df0_agg, df1_agg], ignore_index=True)

# Municipio in target is int, so rename CodMunicipio to Municipio and use it as int Municipio
df_all['Municipio_int'] = df_all['CodMunicipio']

# CP: fill NaN with 0 for aggregation, will keep as int after
df_all['CP'] = df_all['CP'].fillna(0).astype(int)

# SumPoblacion: sum of Poblacion (from df0) plus 0 from df1 rows
df_all['Poblacion'] = pd.to_numeric(df_all['Poblacion'], errors='coerce').fillna(0).astype(int)

# Group by CP, Municipio_int, Provincia and sum Poblacion
result = df_all.groupby(['CP', 'Municipio_int', 'Provincia'], dropna=False, as_index=False)['Poblacion'].sum()

# Rename columns to target schema
result = result.rename(columns={'Municipio_int': 'Municipio', 'Poblacion': 'SumPoblacion'})

# Provincia may have NaN if no match found, keep as is

# Convert Provincia to string type (object)
result['Provincia'] = result['Provincia'].astype('string')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_28/target_multisource_mcts.csv", index=False)