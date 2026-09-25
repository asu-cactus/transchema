import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_5/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_5/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_5/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_5/training_3.csv", index_col=0)

src0['FAP_CONTR'] = pd.to_datetime(src0['FAP_CONTR'], format='%d%b%Y', errors='coerce').dt.strftime('%Y%m%d').astype('Int64')

src2['estado_cli'] = src2['estado_cli'].map({'A':1, 'M':2}).astype('Int64')

src3['XTI_ESTADO'] = src3['XTI_ESTADO'].map({'A':1}).astype('Int64')

join_0 = pd.merge(src3, src0, on='COD_IDCONTRA', how='inner')

join_1 = pd.merge(join_0, src2, on='COD_PERSONA', how='inner')

join_2 = pd.merge(join_1, src1, on='COD_OFICI', how='inner')

result = join_2.rename(columns={
    'COD_PERSONA': 'COD_PERSONA',
    'COD_AREANEGO': 'COD_AREANEGO',
    'COD_EDAD': 'COD_EDAD',
    'COD_OFICIPAL': 'COD_OFICIPAL',
    'COD_SEGLOBAL': 'COD_SEGLOBAL',
    'estado_cli': 'estado_cli',
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
    'FAP_CONTR': 'FAP_CONTR',
    'IMP_CAPDIS': 'IMP_CAPDIS',
    'IMP_CAPINI': 'IMP_CAPINI',
    'IMP_CAPPEN': 'IMP_CAPPEN',
    'COD_PERSONA_x': 'COD_PERSONA_x',
    'COD_PERSONA_y': 'COD_PERSONA_y',
    'XTI_ESTADO': 'XTI_ESTADO',
    'QNU_ORDTIT': 'QNU_ORDTIT',
    'COD_INTERV': 'COD_INTERV'
})

result = result[['COD_INTERV', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD', 'COD_OFICIPAL', 'COD_SEGLOBAL', 'estado_cli', 'COD_OFICI', 'COD_NIVELOFIC', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ', 'cod_areanego', 'des_areanego', 'COD_IDCONTRA', 'COD_PERSONA_x', 'FAP_CONTR', 'IMP_CAPDIS', 'IMP_CAPINI', 'IMP_CAPPEN', 'COD_PERSONA_y', 'XTI_ESTADO', 'QNU_ORDTIT']]

result['COD_PERSONA'] = result['COD_PERSONA'].astype('Int64')
result['COD_AREANEGO'] = result['COD_AREANEGO'].astype('Int64')
result['COD_EDAD'] = result['COD_EDAD'].astype('Int64')
result['COD_OFICIPAL'] = result['COD_OFICIPAL'].astype('Int64')
result['COD_SEGLOBAL'] = result['COD_SEGLOBAL'].astype('Int64')
result['estado_cli'] = result['estado_cli'].astype('Int64')
result['COD_OFICI'] = result['COD_OFICI'].astype('Int64')
result['COD_NIVELOFIC'] = result['COD_NIVELOFIC'].astype('Int64')
result['cod_cbc'] = result['cod_cbc'].astype('Int64')
result['cod_zona'] = result['cod_zona'].astype('Int64')
result['COD_TERRIT'] = result['COD_TERRIT'].astype('Int64')
result['cod_areanego'] = result['cod_areanego'].astype('Int64')
result['COD_IDCONTRA'] = result['COD_IDCONTRA'].astype('Int64')
result['COD_PERSONA_x'] = result['COD_PERSONA_x'].astype('Int64')
result['FAP_CONTR'] = result['FAP_CONTR'].astype('Int64')
result['IMP_CAPDIS'] = result['IMP_CAPDIS'].astype('Int64')
result['IMP_CAPINI'] = result['IMP_CAPINI'].astype('Int64')
result['IMP_CAPPEN'] = result['IMP_CAPPEN'].astype('Int64')
result['COD_PERSONA_y'] = result['COD_PERSONA_y'].astype('Int64')
result['XTI_ESTADO'] = result['XTI_ESTADO'].astype('Int64')
result['QNU_ORDTIT'] = result['QNU_ORDTIT'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_5/target_multisource_mcts.csv", index=False)