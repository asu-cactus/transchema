import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)

dog_stage_cols = ['doggo', 'floofer', 'pupper', 'puppo']
df_melted = df_union.melt(id_vars=[], value_vars=dog_stage_cols, var_name='dog_stage', value_name='dog_type_str')
df_filtered = df_melted[df_melted['dog_type_str'].notna()]

dog_type_map = {'doggo': 2, 'floofer': 4, 'pupper': 3, 'puppo': 4}
df_filtered['dog_type'] = df_filtered['dog_stage'].map(dog_type_map)

result = df_filtered[['dog_type']].reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)