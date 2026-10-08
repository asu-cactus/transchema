import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_19/training_0.csv", index_col=0)
df0['Dates'] = pd.to_datetime(df0['Dates']).dt.day

df_unpivot = df0.melt(id_vars=['Dates'], value_vars=['Action'], var_name='Action', value_name='Action_value')
df_unpivot['Action'] = df_unpivot['Action_value'].astype('category').cat.codes

result = df_unpivot.groupby('Dates', as_index=False)['Action'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_19/target_multisource_mcts.csv", index=False)