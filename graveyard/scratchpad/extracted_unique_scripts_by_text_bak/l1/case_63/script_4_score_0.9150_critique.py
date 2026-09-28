import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_63/training_1.csv", index_col=0)

# Join on 'State'
merged = pd.merge(df0, df1, on='State', how='inner')

# Rename columns to match target schema exactly
merged = merged.rename(columns={
    'Participation_x': 'Participation_x',  # no change needed, but source has 'Participation' only
    'Participation': 'Participation_x',    # from df0
    'Participation_y': 'Participation_y',  # from df1
    'Math_x': 'Math_x',                    # from df0
    'Math_y': 'Math_y'                     # from df1
})

# Because both sources have 'Participation' column, after merge pandas will suffix them automatically.
# So we rename accordingly:
merged = merged.rename(columns={
    'Participation_x': 'Participation_x',  # from df0
    'Participation_y': 'Participation_y'   # from df1
})

# Actually, after merge, pandas will suffix columns with _x and _y automatically for overlapping columns.
# So we just rename 'Participation_x' and 'Participation_y' to match target schema.

# The columns from df0: ['State', 'Participation', 'English', 'Math', 'Reading', 'Science', 'Composite']
# The columns from df1: ['State', 'Participation', 'Evidence-Based Reading and Writing', 'Math', 'Total']

# After merge, columns will be:
# 'State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
# 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total'

# Ensure 'Evidence-Based Reading and Writing', 'Math_y', 'Total' are integer type as in target
merged['Evidence-Based Reading and Writing'] = merged['Evidence-Based Reading and Writing'].astype('Int64')
merged['Math_y'] = merged['Math_y'].astype('Int64')
merged['Total'] = merged['Total'].astype('Int64')

# Select columns in target schema order
cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
        'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

result = merged[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_63/target_multisource_mcts.csv", index=False)