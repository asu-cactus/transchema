import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_36/training_0.csv", index_col=0)

df_long = df.melt(id_vars=['Date', 'Day'], var_name='variable', value_name='value')

# Do NOT drop NaN values in 'value' column

df_long['variable'] = df_long['variable'].str.split('_')

df_result = df_long[['variable']].reset_index(drop=True)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length5_36/target_multisource_mcts.csv", index=False)