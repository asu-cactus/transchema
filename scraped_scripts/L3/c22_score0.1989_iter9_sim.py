import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=[col for col in df0.columns if col != 'Reg Count' and col != 'Term'],
                      value_vars=['Reg Count'],
                      var_name='Term',
                      value_name='Value')

df_unpivot['Term'] = df0['Term']

df_grouped = df_unpivot.groupby(['Department', 'Term'], as_index=False)['Value'].sum()

df_pivot = df_grouped.pivot(index='Department', columns='Term', values='Value')

df_pivot = df_pivot.rename_axis(None, axis=1).reset_index()

target_terms = ['20153', '20161', '20162']
for term in target_terms:
    if term not in df_pivot.columns:
        df_pivot[term] = pd.NA

df_result = df_pivot[['Department'] + target_terms]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length3_22/target_multisource_mcts.csv", index=False)