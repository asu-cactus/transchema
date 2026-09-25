import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_1/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_1/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_1/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_1/training_3.csv", index_col=0)

r0 = pd.merge(s2, s3, how='inner', left_on=['COD_IDCONTRA', 'COD_PERSONA'], right_on=['COD_IDCONTRA', 'COD_PERSONA'], suffixes=('_x', '_y'))
r1 = pd.merge(r0, s1, how='inner', left_on='COD_PERSONA', right_on='COD_PERSONA', suffixes=('', '_y'))
r2 = pd.merge(r1, s0, how='inner', left_on='COD_OFICI', right_on='COD_OFICI', suffixes=('', '_y'))

r2 = r2.rename(columns={
    'COD_PERSONA': 'COD_PERSONA',
    'COD_PERSONA_x': 'COD_PERSONA_x',
    'COD_PERSONA_y': 'COD_PERSONA_y'
})

target_cols = ['COD_INTERV', 'FAP_CONTR', 'estado_cli', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD', 'COD_OFICIPAL', 'COD_SEGLOBAL', 'COD_OFICI', 'COD_NIVELOFIC', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ', 'cod_areanego', 'des_areanego', 'COD_IDCONTRA', 'COD_PERSONA_x', 'IMP_CAPDIS', 'IMP_CAPINI', 'IMP_CAPPEN', 'COD_PERSONA_y', 'XTI_ESTADO', 'QNU_ORDTIT']

result = r2[target_cols]

result['COD_PERSONA'] = result['COD_PERSONA'].astype('Int64')
result['COD_AREANEGO'] = result['COD_AREANEGO'].astype('Int64')
result['COD_EDAD'] = result['COD_EDAD'].astype('Int64')
result['COD_OFICIPAL'] = result['COD_OFICIPAL'].astype('Int64')
result['COD_SEGLOBAL'] = result['COD_SEGLOBAL'].astype('Int64')
result['COD_OFICI'] = result['COD_OFICI'].astype('Int64')
result['COD_NIVELOFIC'] = result['COD_NIVELOFIC'].astype('Int64')
result['des_ofici'] = result['des_ofici'].astype('Int64')
result['cod_cbc'] = result['cod_cbc'].astype('Int64')
result['des_cbc'] = result['des_cbc'].astype('Int64')
result['cod_zona'] = result['cod_zona'].astype('Int64')
result['des_zona'] = result['des_zona'].astype('Int64')
result['COD_TERRIT'] = result['COD_TERRIT'].astype('Int64')
result['des_territ'] = result['des_territ'].astype('Int64')
result['cod_areanego'] = result['cod_areanego'].astype('Int64')
result['des_areanego'] = result['des_areanego'].astype('Int64')
result['COD_IDCONTRA'] = result['COD_IDCONTRA'].astype('Int64')
result['COD_PERSONA_x'] = result['COD_PERSONA_x'].astype('Int64')
result['IMP_CAPDIS'] = result['IMP_CAPDIS'].astype('Int64')
result['IMP_CAPINI'] = result['IMP_CAPINI'].astype('Int64')
result['IMP_CAPPEN'] = result['IMP_CAPPEN'].astype('Int64')
result['COD_PERSONA_y'] = result['COD_PERSONA_y'].astype('Int64')
result['XTI_ESTADO'] = result['XTI_ESTADO'].astype('Int64')
result['QNU_ORDTIT'] = result['QNU_ORDTIT'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_1/target_multisource_mcts.csv", index=False)