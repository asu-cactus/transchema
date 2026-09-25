import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_4/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=['fname'], value_vars=['Slice n°', 'X', 'Y', 'Distance', 'Pixel Value', 'ok_col_names', 'ok_col_num', 'ok_row_num', 'cop_name', 'day'], var_name='variable', value_name='value')

result = df_unpivot.groupby('fname').size().reset_index(name='count_of_obs')
result['count_of_obs'] = result['count_of_obs'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts.csv", index=False)