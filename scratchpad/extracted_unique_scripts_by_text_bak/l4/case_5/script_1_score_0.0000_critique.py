import pandas as pd

# Read sources with index_col=0 as per hint 22
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_5/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_5/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_5/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_5/training_3.csv', index_col=0)

# Join Source3 and Source0 on COD_IDCONTRA and COD_PERSONA
df = pd.merge(source3, source0, on=['COD_IDCONTRA', 'COD_PERSONA'], how='inner')

# Join with Source2 on COD_PERSONA
df = pd.merge(df, source2, on='COD_PERSONA', how='inner')

# Join with Source1 on Source2.COD_OFICIPAL = Source1.COD_OFICI
df = pd.merge(df, source1, left_on='COD_OFICIPAL', right_on='COD_OFICI', how='inner')

# Convert estado_cli from string to categorical integer codes
df['estado_cli'] = df['estado_cli'].astype('category').cat.codes

# Aggregate columns:
# Group by leftmost columns (keys) as per plan
group_by_cols = [
    'COD_INTERV', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD', 'COD_OFICIPAL', 'COD_SEGLOBAL',
    'estado_cli', 'COD_OFICI', 'COD_NIVELOFIC', 'des_ofici', 'cod_cbc', 'des_cbc',
    'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ', 'cod_areanego', 'des_areanego',
    'COD_IDCONTRA', 'COD_PERSONA_x', 'COD_PERSONA_y', 'XTI_ESTADO', 'QNU_ORDTIT'
]

# For FAP_CONTR (date string), take first (assuming same per group)
# For IMP_CAPDIS, IMP_CAPINI, IMP_CAPPEN sum aggregation
agg_dict = {
    'FAP_CONTR': 'first',
    'IMP_CAPDIS': 'sum',
    'IMP_CAPINI': 'sum',
    'IMP_CAPPEN': 'sum'
}

# Perform groupby aggregation
result = df.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
target_columns = [
    'COD_INTERV', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD', 'COD_OFICIPAL', 'COD_SEGLOBAL',
    'estado_cli', 'COD_OFICI', 'COD_NIVELOFIC', 'des_ofici', 'cod_cbc', 'des_cbc',
    'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ', 'cod_areanego', 'des_areanego',
    'COD_IDCONTRA', 'COD_PERSONA_x', 'FAP_CONTR', 'IMP_CAPDIS', 'IMP_CAPINI', 'IMP_CAPPEN',
    'COD_PERSONA_y', 'XTI_ESTADO', 'QNU_ORDTIT'
]

# Some columns may be missing if not in df after aggregation, ensure all present
for col in target_columns:
    if col not in result.columns:
        result[col] = pd.NA

result = result[target_columns]

# Write to CSV
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_5/target_multisource_mcts.csv', index=False)