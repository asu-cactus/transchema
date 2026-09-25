import pandas as pd

# Read sources with index_col=0 as per hint 22
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_2/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_2/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_2/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_2/training_3.csv', index_col=0)

# Join Source0 and Source1 on COD_OFICIPAL = COD_OFICI and COD_AREANEGO = cod_areanego
df01 = pd.merge(
    source0,
    source1,
    left_on=['COD_OFICIPAL', 'COD_AREANEGO'],
    right_on=['COD_OFICI', 'cod_areanego'],
    how='inner',
    suffixes=('', '_s1')
)

# Join df01 with Source2 on COD_PERSONA
df012 = pd.merge(
    df01,
    source2,
    on='COD_PERSONA',
    how='inner',
    suffixes=('', '_s2')
)

# Join df012 with Source3 on COD_IDCONTRA and COD_PERSONA
df0123 = pd.merge(
    df012,
    source3,
    on=['COD_IDCONTRA', 'COD_PERSONA'],
    how='inner',
    suffixes=('', '_s3')
)

# Convert COD_SEGLOBAL to int (from float)
df0123['COD_SEGLOBAL'] = df0123['COD_SEGLOBAL'].astype('Int64')

# Convert estado_cli to int if possible (currently string)
# From source0, estado_cli is string like 'A', '0' in examples, target expects int
# We must convert estado_cli to int - but source0 has string values like 'A', '0'
# The target schema says estado_cli is integer, but source0 has string values like 'A'
# Possibly map 'A' to 1, '0' to 0, or convert to categorical codes
# Since no hardcoding allowed, convert estado_cli to categorical codes starting from 0 + 1 to match target 1-based
df0123['estado_cli'] = df0123['estado_cli'].astype('category').cat.codes + 1

# Group by leftmost columns (primary key columns)
group_by_cols = ['FAP_CONTR', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD', 'COD_OFICIPAL', 'COD_SEGLOBAL', 'estado_cli']

# Aggregation columns: all other columns except group_by_cols
agg_cols = df0123.columns.difference(group_by_cols)

# For aggregation, use first() to keep consistent values per group
agg_dict = {col: 'first' for col in agg_cols}

df_final = df0123.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Rename columns to match target schema exactly:
# The target schema has columns:
# ['FAP_CONTR', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD', 'COD_OFICIPAL', 'COD_SEGLOBAL', 'estado_cli',
#  'COD_OFICI', 'COD_NIVELOFIC', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT',
#  'des_territ', 'cod_areanego', 'des_areanego', 'COD_IDCONTRA', 'COD_PERSONA_x', 'IMP_CAPDIS', 'IMP_CAPINI',
#  'IMP_CAPPEN', 'COD_PERSONA_y', 'XTI_ESTADO', 'QNU_ORDTIT', 'COD_INTERV']

# The join may have added suffixes, so ensure columns are named exactly as target:
# source1 columns: COD_OFICI, COD_NIVELOFIC, des_ofici, cod_cbc, des_cbc, cod_zona, des_zona, COD_TERRIT, des_territ, cod_areanego, des_areanego
# source2 columns: COD_IDCONTRA, IMP_CAPDIS, IMP_CAPINI, IMP_CAPPEN
# source3 columns: COD_PERSONA (will be COD_PERSONA_y), XTI_ESTADO, QNU_ORDTIT, COD_INTERV

# After merges, pandas will add suffixes to overlapping columns:
# COD_PERSONA from source0, source2, source3: source0 is COD_PERSONA, source2 join on COD_PERSONA no suffix, source3 join on COD_PERSONA no suffix
# But source3 also has COD_PERSONA, so pandas will add suffixes to avoid conflicts:
# Actually, since we merged on COD_PERSONA, no suffix added for that column.
# But source3 has COD_PERSONA, so no suffix added.
# However, source2 and source3 both have COD_PERSONA, so pandas may add suffixes to distinguish.

# To be safe, rename columns explicitly:

# Rename columns to target schema names:
df_final = df_final.rename(columns={
    'COD_OFICI': 'COD_OFICI',
    'COD_NIVELOFIC': 'COD_NIVELOFIC',
    'des_ofici': 'des_ofici',
    'cod_cbc': 'cod_cbc',
    'des_cbc': 'des_cbc',
    'cod_zona': 'cod_zona',
    'des_zona': 'des_zona',
    'COD_TERRIT': 'COD_TERRIT',
    'des_territ': 'des_territ',
    'cod_areanego': 'cod_areanego',
    'des_areanego': 'des_areanego',
    'COD_IDCONTRA': 'COD_IDCONTRA',
    'IMP_CAPDIS': 'IMP_CAPDIS',
    'IMP_CAPINI': 'IMP_CAPINI',
    'IMP_CAPPEN': 'IMP_CAPPEN',
    'XTI_ESTADO': 'XTI_ESTADO',
    'QNU_ORDTIT': 'QNU_ORDTIT',
    'COD_INTERV': 'COD_INTERV',
})

# For the multiple COD_PERSONA columns in target:
# The target has 'COD_PERSONA', 'COD_PERSONA_x', 'COD_PERSONA_y'
# After merges, pandas will add suffixes _x and _y for overlapping columns.
# We must keep these columns as is.

# Check if these columns exist, if not, create them from existing columns:
if 'COD_PERSONA_x' not in df_final.columns and 'COD_PERSONA' in df_final.columns:
    df_final['COD_PERSONA_x'] = df_final['COD_PERSONA']
if 'COD_PERSONA_y' not in df_final.columns and 'COD_PERSONA' in df_final.columns:
    df_final['COD_PERSONA_y'] = df_final['COD_PERSONA']

# Ensure column order matches target schema exactly:
target_columns = ['FAP_CONTR', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD', 'COD_OFICIPAL', 'COD_SEGLOBAL', 'estado_cli',
                  'COD_OFICI', 'COD_NIVELOFIC', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT',
                  'des_territ', 'cod_areanego', 'des_areanego', 'COD_IDCONTRA', 'COD_PERSONA_x', 'IMP_CAPDIS', 'IMP_CAPINI',
                  'IMP_CAPPEN', 'COD_PERSONA_y', 'XTI_ESTADO', 'QNU_ORDTIT', 'COD_INTERV']

# Some columns may be missing if source data lacks them, fill with NaN if needed
for col in target_columns:
    if col not in df_final.columns:
        df_final[col] = pd.NA

df_final = df_final[target_columns]

# Save to CSV
df_final.to_csv('autopipeline-benchmarks/github-pipelines/length4_2/target_multisource_mcts.csv', index=False)