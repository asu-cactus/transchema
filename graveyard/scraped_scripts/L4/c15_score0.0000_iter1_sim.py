import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_0.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_3.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_2.csv", index_col=0)

df0 = src0[['COD_INTERV', 'XTI_ESTADO']].rename(columns={'XTI_ESTADO': 'estado_cli'})
df0['COD_OFICI'] = pd.NA
df0['COD_NIVELOFIC'] = pd.NA

df3 = src3[['estado_cli', 'COD_OFICIPAL']].rename(columns={'COD_OFICIPAL': 'COD_OFICI'})
df3['COD_INTERV'] = pd.NA
df3['COD_NIVELOFIC'] = pd.NA

union_result = pd.concat([df0, df3], ignore_index=True, sort=False)

union_result['COD_OFICI'] = pd.to_numeric(union_result['COD_OFICI'], errors='coerce').astype('Int64')

joined = union_result.merge(src2[['COD_OFICI', 'COD_NIVELOFIC']], on='COD_OFICI', how='left')

joined = joined[['COD_INTERV', 'estado_cli', 'COD_OFICI', 'COD_NIVELOFIC']]

print(joined.dtypes)

joined.to_csv("autopipeline-benchmarks/github-pipelines/length4_15/target_multisource_mcts.csv", index=False)