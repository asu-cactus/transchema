import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_83/training_0.csv', index_col=0)
df0 = df0.rename(columns={'Fare': 'price'})
df0['date'] = ''
df_target = df0[['date', 'price']]
df_target.to_csv('autopipeline-benchmarks/github-pipelines/length2_83/target_multisource_mcts.csv', index=False)