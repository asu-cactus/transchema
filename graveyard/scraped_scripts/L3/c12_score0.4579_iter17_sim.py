import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_12/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=['SN', 'Price'], value_vars=['Purchase ID', 'Age', 'Gender', 'Item ID', 'Item Name'],
                      var_name='variable', value_name='count')

df_unpivot['count'] = 1
result = df_unpivot[['SN', 'Price', 'count']]

result['SN'] = result['SN'].astype(str)
result['Price'] = result['Price'].astype(float)
result['count'] = result['count'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_12/target_multisource_mcts.csv", index=False)