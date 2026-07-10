import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_45/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_45/training_1.csv", index_col=0)

df0 = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

df1 = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

df = pd.merge(df0, df1, on='State', how='inner')

# Group by 'State' and aggregate accordingly
agg_dict = {
    'Participation_x': 'first',
    'English': 'mean',
    'Math_x': 'mean',
    'Reading': 'mean',
    'Science': 'mean',
    'Composite': 'mean',
    'Participation_y': 'first',
    'Evidence-Based Reading and Writing': 'mean',
    'Math_y': 'mean',
    'Total': 'mean'
}

df = df.groupby('State', as_index=False).agg(agg_dict)

# Ensure column order matches target schema exactly
df = df[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
         'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

# Cast integer columns to int (since mean returns float)
int_cols = ['Evidence-Based Reading and Writing', 'Math_y', 'Total']
df[int_cols] = df[int_cols].round().astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_45/target_multisource_mcts.csv", index=False)