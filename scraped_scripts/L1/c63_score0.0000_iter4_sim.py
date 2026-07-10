import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_63/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=['State', 'Participation'], 
                       value_vars=['English', 'Math', 'Reading', 'Science', 'Composite'], 
                       var_name='Participation_y', value_name='Score')

df0_pivot = df0_unpivot.pivot_table(index=['State', 'Participation', 'Participation_y'], 
                                   columns='Participation_y', values='Score', aggfunc='first').reset_index()

df0_pivot.rename(columns={'Participation': 'Participation_x', 'Math': 'Math_x'}, inplace=True)

df_merged = pd.merge(df0_pivot, df1, how='inner', left_on=['State', 'Participation_y'], right_on=['State', 'Participation'])

df_merged.rename(columns={'Participation_x': 'Participation_x',
                          'English': 'English',
                          'Math_x': 'Math_x',
                          'Reading': 'Reading',
                          'Science': 'Science',
                          'Composite': 'Composite',
                          'Participation_y': 'Participation_y',
                          'Evidence-Based Reading and Writing': 'Evidence-Based Reading and Writing',
                          'Math': 'Math_y',
                          'Total': 'Total'}, inplace=True)

df_merged = df_merged[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                       'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_63/target_multisource_mcts.csv", index=False)