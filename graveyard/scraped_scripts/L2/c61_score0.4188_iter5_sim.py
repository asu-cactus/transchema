import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_61/training_0.csv", index_col=0)

df_pivot = df0.melt(var_name='variable', value_name='value')
df_pivot['0'] = 0  # dummy group key for groupby

df_grouped = df_pivot.groupby('0').apply(lambda g: pd.Series({
    '0': g.loc[g['variable'] == '0', 'value'].values[0],
    '1': g.loc[g['variable'] == '1', 'value'].values[0],
    '2': g.loc[g['variable'] == '2', 'value'].values[0],
    '3': g.loc[g['variable'] == '3', 'value'].values[0],
})).reset_index(drop=True)

df_grouped = df_grouped.astype(float)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_61/target_multisource_mcts.csv", index=False)