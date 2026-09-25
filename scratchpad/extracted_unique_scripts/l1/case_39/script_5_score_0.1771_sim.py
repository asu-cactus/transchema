import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

agg0 = df0.groupby('Participation', as_index=False).agg({
    'English': 'mean',
    'Math': 'mean',
    'Reading': 'mean',
    'Science': 'mean',
    'Composite': 'mean'
}).rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

agg1 = df1.groupby('Participation', as_index=False).agg({
    'Evidence-Based Reading and Writing': 'mean',
    'Math': 'mean',
    'Total': 'mean'
}).rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y',
    'Evidence-Based Reading and Writing': 'Evidence-Based Reading and Writing',
    'Total': 'Total'
})

result = pd.merge(agg0, agg1, left_on='Participation_x', right_on='Participation_y', how='inner')

result['Evidence-Based Reading and Writing'] = result['Evidence-Based Reading and Writing'].round().astype('Int64')
result['Math_y'] = result['Math_y'].round().astype('Int64')
result['Total'] = result['Total'].round().astype('Int64')

result['State'] = None

cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite', 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']
result = result[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)