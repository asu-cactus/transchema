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

result = pd.concat([df0_final, df1_final], ignore_index=True)

result['Evidence-Based Reading and Writing'] = pd.to_numeric(result['Evidence-Based Reading and Writing'], errors='coerce').astype('Int64')
result['Math_y'] = pd.to_numeric(result['Math_y'], errors='coerce').astype('Int64')
result['Total'] = pd.to_numeric(result['Total'], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)