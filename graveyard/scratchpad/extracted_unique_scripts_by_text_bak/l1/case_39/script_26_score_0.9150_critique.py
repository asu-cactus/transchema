import pandas as pd

# Read source tables with index_col=0 to ignore the first index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

# Merge on 'State' with suffixes to match target schema
df = pd.merge(df0, df1, on="State", suffixes=('_x', '_y'))

# Select columns exactly as in target schema
df = df[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
         'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

# Write to target CSV
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)