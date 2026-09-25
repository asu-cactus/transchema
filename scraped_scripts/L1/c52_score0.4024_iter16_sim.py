import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)
df0_filtered = df0[df0['click'] == 1]
df_union = pd.concat([df0_filtered, df0_filtered], ignore_index=True)
df_union = df_union.rename(columns={'condition': 'condition', 'click': '0'})
df_result = df_union[['condition', '0']].copy()
df_result['0'] = df_result['0'].astype(int)
df_result['condition'] = df_result['condition'].astype(int)
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)