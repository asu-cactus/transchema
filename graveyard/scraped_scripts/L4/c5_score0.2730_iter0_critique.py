import pandas as pd

# Read source tables with index_col=0 as per hint 22
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_5/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_5/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_5/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_5/training_3.csv', index_col=0)

# Join Source4_5_3 and Source4_5_0 on COD_IDCONTRA and COD_PERSONA
df = pd.merge(source3, source0, how='inner', on=['COD_IDCONTRA', 'COD_PERSONA'])

# Join the result with Source4_5_2 on COD_PERSONA
df = pd.merge(df, source2, how='inner', on='COD_PERSONA')

# Join the result with Source4_5_1 on COD_OFICIPAL (from source2) = COD_OFICI (from source1)
df = pd.merge(df, source1, how='inner', left_on='COD_OFICIPAL', right_on='COD_OFICI')

# Group by the leftmost columns of the target schema that are string or integer and unique
group_by_cols = ['COD_INTERV', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD', 'COD_OFICIPAL', 'COD_SEGLOBAL', 'estado_cli']

# No aggregation columns specified, so just drop duplicates by group_by columns to match target uniqueness
df = df.drop_duplicates(subset=group_by_cols)

# Select and reorder columns exactly as in the target schema
target_columns = ['COD_INTERV', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD', 'COD_OFICIPAL', 'COD_SEGLOBAL', 'estado_cli',
                  'COD_OFICI', 'COD_NIVELOFIC', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT',
                  'des_territ', 'cod_areanego', 'des_areanego', 'COD_IDCONTRA', 'COD_PERSONA_x', 'FAP_CONTR', 'IMP_CAPDIS',
                  'IMP_CAPINI', 'IMP_CAPPEN', 'COD_PERSONA_y', 'XTI_ESTADO', 'QNU_ORDTIT']

# Rename columns to match target schema where needed:
# After merges, pandas adds suffixes _x and _y for overlapping columns.
# We have COD_PERSONA from multiple tables, so rename accordingly:
df = df.rename(columns={
    'COD_PERSONA_x': 'COD_PERSONA_x',
    'COD_PERSONA_y': 'COD_PERSONA_y',
    'COD_OFICI': 'COD_OFICI',  # from source1
    'des_ofici': 'des_ofici',
    'COD_NIVELOFIC': 'COD_NIVELOFIC',
    'cod_cbc': 'cod_cbc',
    'des_cbc': 'des_cbc',
    'cod_zona': 'cod_zona',
    'des_zona': 'des_zona',
    'COD_TERRIT': 'COD_TERRIT',
    'des_territ': 'des_territ',
    'cod_areanego': 'cod_areanego',
    'des_areanego': 'des_areanego',
    'FAP_CONTR': 'FAP_CONTR',
    'IMP_CAPDIS': 'IMP_CAPDIS',
    'IMP_CAPINI': 'IMP_CAPINI',
    'IMP_CAPPEN': 'IMP_CAPPEN',
    'XTI_ESTADO': 'XTI_ESTADO',
    'QNU_ORDTIT': 'QNU_ORDTIT'
})

# Some columns like COD_PERSONA_x and COD_PERSONA_y come from merges, keep as is.

# Select columns in order, some columns may not exist if source data is missing them, so use reindex with columns and allow missing columns
df = df.reindex(columns=target_columns)

# Write to CSV
df.to_csv('autopipeline-benchmarks/github-pipelines/length4_5/target_multisource_mcts.csv', index=False)