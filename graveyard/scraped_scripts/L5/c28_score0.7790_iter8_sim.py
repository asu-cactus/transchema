import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_1.csv", index_col=0)

agg_source0 = source0.groupby(['CodProvincia', 'CodMunicipio', 'Provincia'], as_index=False)['Poblacion'].sum()

merged = pd.merge(agg_source0, source1, on=['CodProvincia', 'CodMunicipio'], how='inner')

result = merged[['CP', 'CodMunicipio', 'Poblacion', 'Provincia']].copy()
result.columns = ['CP', 'Municipio', 'SumPoblacion', 'Provincia']
result['CP'] = result['CP'].astype(int)
result['Municipio'] = result['Municipio'].astype(int)
result['SumPoblacion'] = result['SumPoblacion'].astype(int)
result['Provincia'] = result['Provincia'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_28/target_multisource_mcts.csv", index=False)