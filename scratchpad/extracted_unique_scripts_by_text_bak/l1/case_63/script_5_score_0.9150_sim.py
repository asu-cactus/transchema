import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_63/training_1.csv", index_col=0)

df0['Participation'] = df0['Participation'].str.rstrip('%').astype(float)
agg0 = df0.groupby('State').agg({
    'Participation': 'mean',
    'English': 'mean',
    'Math': 'mean',
    'Reading': 'mean',
    'Science': 'mean',
    'Composite': 'mean'
}).reset_index()

agg0['Participation_x'] = agg0['Participation'].round(0).astype(int).astype(str) + '%'
agg0.rename(columns={'Math': 'Math_x'}, inplace=True)
agg0.drop(columns=['Participation'], inplace=True)

df1['Participation_y'] = df1['Participation']
df1.drop(columns=['Participation'], inplace=True)

df1['Evidence-Based Reading and Writing'] = df1['Evidence-Based Reading and Writing'].astype(int)
df1['Math_y'] = df1['Math'].astype(int)
df1['Total'] = df1['Total'].astype(int)
df1.drop(columns=['Math'], inplace=True)

result = pd.merge(agg0, df1, on='State', how='inner')

result = result[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_63/target_multisource_mcts.csv", index=False)