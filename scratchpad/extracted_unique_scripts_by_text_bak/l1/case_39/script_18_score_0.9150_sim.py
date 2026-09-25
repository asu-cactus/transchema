import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={'Participation': 'Participation_x', 'Math': 'Math_x'})

df1_renamed = df1.rename(columns={'Participation': 'Participation_y', 'Math': 'Math_y'})

df0_melted = df0_renamed.melt(id_vars=['State', 'Participation_x'], var_name='Subject', value_name='Score')

df0_pivot = df0_melted.pivot(index=['State', 'Participation_x'], columns='Subject', values='Score').reset_index()

df_merged = pd.merge(df0_pivot, df1_renamed, how='inner', on='State')

df_final = df_merged[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                      'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)