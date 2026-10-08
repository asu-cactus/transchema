import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

df1_renamed = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

union_cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite']
df0_sub = df0_renamed[union_cols]

# For df1, create missing columns with NaN or appropriate dtypes to match union_cols
df1_sub = df1_renamed.copy()
df1_sub['English'] = pd.NA
df1_sub['Reading'] = pd.NA
df1_sub['Science'] = pd.NA
df1_sub['Composite'] = pd.NA
df1_sub = df1_sub.rename(columns={'Participation_y': 'Participation_x', 'Math_y': 'Math_x'})
df1_sub = df1_sub[union_cols]

union_result = pd.concat([df0_sub, df1_sub], ignore_index=True)

df1_for_join = df1_renamed.copy()

final = pd.merge(
    union_result,
    df1_for_join[['State', 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']],
    on='State',
    how='inner'
)

final = final[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
               'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

final['Evidence-Based Reading and Writing'] = final['Evidence-Based Reading and Writing'].astype('Int64')
final['Participation_x'] = final['Participation_x'].astype(str)
final['Participation_y'] = final['Participation_y'].astype(str)

final.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)