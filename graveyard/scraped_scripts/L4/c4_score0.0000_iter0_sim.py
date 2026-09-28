import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_4/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_4/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_4/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_4/training_3.csv", index_col=0)

join_0_1 = pd.merge(src0, src1, how='inner', left_on=['COD_IDCONTRA', 'COD_PERSONA'], right_on=['COD_IDCONTRA', 'COD_PERSONA'], suffixes=('_x', '_y'))
join_0_1_3 = pd.merge(join_0_1, src3, how='inner', left_on='COD_PERSONA', right_on='COD_PERSONA', suffixes=('', '_3'))
final = pd.merge(join_0_1_3, src2, how='inner', left_on='COD_OFICI', right_on='COD_OFICI', suffixes=('', '_2'))

final = final.rename(columns={
    'estado_cli': 'estado_cli',
    'COD_INTERV': 'COD_INTERV',
    'COD_PERSONA': 'COD_PERSONA',
    'COD_AREANEGO': 'COD_AREANEGO',
    'COD_EDAD': 'COD_EDAD',
    'COD_OFICIPAL': 'COD_OFICIPAL',
    'COD_SEGLOBAL': 'COD_SEGLOBAL',
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
    'FAP_CONTR': 'FAP_CONTR',
    'COD_PERSONA_x': 'COD_PERSONA_x',
    'COD_PERSONA_y': 'COD_PERSONA_y'
}, errors='ignore')

cols = ['FAP_CONTR', 'estado_cli', 'COD_INTERV', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD', 'COD_OFICIPAL', 'COD_SEGLOBAL', 'COD_OFICI', 'COD_NIVELOFIC', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ', 'cod_areanego', 'des_areanego', 'COD_IDCONTRA', 'COD_PERSONA_x', 'IMP_CAPDIS', 'IMP_CAPINI', 'IMP_CAPPEN', 'COD_PERSONA_y', 'XTI_ESTADO', 'QNU_ORDTIT']

result = final[cols]

# Convert types according to target schema
result['FAP_CONTR'] = result['FAP_CONTR'].astype(str)
result['estado_cli'] = result['estado_cli'].astype(str)
result['COD_INTERV'] = result['COD_INTERV'].astype(str)
result['COD_PERSONA'] = pd.to_numeric(result['COD_PERSONA'], errors='coerce').astype('Int64')
result['COD_AREANEGO'] = pd.to_numeric(result['COD_AREANEGO'], errors='coerce').astype('Int64')
result['COD_EDAD'] = pd.to_numeric(result['COD_EDAD'], errors='coerce').astype('Int64')
result['COD_OFICIPAL'] = pd.to_numeric(result['COD_OFICIPAL'], errors='coerce').astype('Int64')
result['COD_SEGLOBAL'] = pd.to_numeric(result['COD_SEGLOBAL'], errors='coerce').astype('Int64')
result['COD_OFICI'] = pd.to_numeric(result['COD_OFICI'], errors='coerce').astype('Int64')
result['COD_NIVELOFIC'] = pd.to_numeric(result['COD_NIVELOFIC'], errors='coerce').astype('Int64')
result['des_ofici'] = pd.to_numeric(result['des_ofici'], errors='coerce').astype('Int64')
result['cod_cbc'] = pd.to_numeric(result['cod_cbc'], errors='coerce').astype('Int64')
result['des_cbc'] = pd.to_numeric(result['des_cbc'], errors='coerce').astype('Int64')
result['cod_zona'] = pd.to_numeric(result['cod_zona'], errors='coerce').astype('Int64')
result['des_zona'] = pd.to_numeric(result['des_zona'], errors='coerce').astype('Int64')
result['COD_TERRIT'] = pd.to_numeric(result['COD_TERRIT'], errors='coerce').astype('Int64')
result['des_territ'] = pd.to_numeric(result['des_territ'], errors='coerce').astype('Int64')
result['cod_areanego'] = pd.to_numeric(result['cod_areanego'], errors='coerce').astype('Int64')
result['des_areanego'] = pd.to_numeric(result['des_areanego'], errors='coerce').astype('Int64')
result['COD_IDCONTRA'] = pd.to_numeric(result['COD_IDCONTRA'], errors='coerce').astype('Int64')
result['COD_PERSONA_x'] = pd.to_numeric(result['COD_PERSONA_x'], errors='coerce').astype('Int64')
result['IMP_CAPDIS'] = pd.to_numeric(result['IMP_CAPDIS'], errors='coerce').astype('Int64')
result['IMP_CAPINI'] = pd.to_numeric(result['IMP_CAPINI'], errors='coerce').astype('Int64')
result['IMP_CAPPEN'] = pd.to_numeric(result['IMP_CAPPEN'], errors='coerce').astype('Int64')
result['COD_PERSONA_y'] = pd.to_numeric(result['COD_PERSONA_y'], errors='coerce').astype('Int64')
result['XTI_ESTADO'] = pd.to_numeric(result['XTI_ESTADO'], errors='coerce').astype('Int64')
result['QNU_ORDTIT'] = pd.to_numeric(result['QNU_ORDTIT'], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_4/target_multisource_mcts.csv", index=False)