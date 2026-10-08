import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_1.csv", index_col=0)

# Clean 'State' columns: strip whitespace and unify case (e.g., title case)
df0['State'] = df0['State'].str.strip()
df1['State'] = df1['State'].str.strip()

# Rename columns to match target schema
df0 = df0.rename(columns={'Participation': 'Participation_x', 'Math': 'Math_x'})
df1 = df1.rename(columns={'Participation': 'Participation_y', 'Math': 'Math_y'})

# Inner join on 'State'
merged = pd.merge(df0, df1, on='State', how='inner')

# Select columns in target schema order
cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
        'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

result = merged[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_25/target_multisource_mcts.csv", index=False)