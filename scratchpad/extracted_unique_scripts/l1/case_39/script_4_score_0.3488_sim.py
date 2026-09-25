import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})
df0_renamed['Participation_y'] = pd.NA
df0_renamed['Evidence-Based Reading and Writing'] = pd.NA
df0_renamed['Math_y'] = pd.NA
df0_renamed['Total'] = pd.NA

df1_renamed = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})
df1_renamed['Participation_x'] = pd.NA
df1_renamed['English'] = pd.NA
df1_renamed['Math_x'] = pd.NA
df1_renamed['Reading'] = pd.NA
df1_renamed['Science'] = pd.NA
df1_renamed['Composite'] = pd.NA

cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
        'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

df0_final = df0_renamed[cols]
df1_final = df1_renamed[cols]

df_union = pd.concat([df0_final, df1_final], ignore_index=True)

df_grouped = df_union.groupby('Participation_y', dropna=False, as_index=False).agg({
    'State': 'first',
    'Participation_x': 'first',
    'English': 'first',
    'Math_x': 'first',
    'Reading': 'first',
    'Science': 'first',
    'Composite': 'first',
    'Evidence-Based Reading and Writing': 'first',
    'Math_y': 'first',
    'Total': 'first'
})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)