import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_1.csv", index_col=0)

df0['Participation'] = df0['Participation'].str.rstrip('%').astype(float)
agg = df0.groupby('State').agg({
    'Participation': 'mean',
    'English': 'mean',
    'Math': 'mean',
    'Reading': 'mean',
    'Science': 'mean',
    'Composite': 'mean'
}).reset_index()

agg['Participation'] = agg['Participation'].round(0).astype(int).astype(str) + '%'
agg.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
}, inplace=True)

df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
}, inplace=True)

df1['Participation_y'] = df1['Participation_y'].astype(str)

result = pd.merge(agg, df1, on='State', how='inner')

result['Evidence-Based Reading and Writing'] = result['Evidence-Based Reading and Writing'].astype('Int64')
result['Math_y'] = result['Math_y'].astype('Int64')
result['Total'] = result['Total'].astype('Int64')

result = result[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_25/target_multisource_mcts.csv", index=False)