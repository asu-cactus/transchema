import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)

df_union = pd.concat([df0], ignore_index=True)

df_pivot = df_union.groupby('condition')['click'].sum().reset_index()

df_pivot.columns = ['condition', '0']
df_pivot['condition'] = df_pivot['condition'].astype(int)
df_pivot['0'] = df_pivot['0'].astype(int)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)