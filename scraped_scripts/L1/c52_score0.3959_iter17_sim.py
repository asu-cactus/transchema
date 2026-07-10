import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)
df_filtered = df0[df0['click'] == 0]
df_union = pd.concat([df_filtered, df_filtered], ignore_index=True)
df_projected = df_union[['condition', 'click']]
df_projected = df_projected.rename(columns={'click': '0'})
df_projected.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)