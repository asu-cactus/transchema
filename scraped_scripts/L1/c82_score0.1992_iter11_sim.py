import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=['scientific_name', 'conservation_status'], value_vars=['category', 'common_names'], 
                      var_name='variable', value_name='value')

result = df0[['conservation_status', 'scientific_name']].copy()
result['scientific_name'] = pd.to_numeric(result['scientific_name'], errors='coerce')

result = result[['conservation_status', 'scientific_name']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)