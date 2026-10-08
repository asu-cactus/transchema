import pandas as pd

# Read source tables, ignoring the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_17/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_17/training_1.csv", index_col=0)

# Reset index to make 'School ID' a column (not index)
df0 = df0.reset_index(drop=True)

# Join on 'school_name'
merged = pd.merge(df0, df1, how='inner', on='school_name')

# Select columns exactly as in target schema
result = merged[['School ID', 'school_name', 'type', 'size', 'budget',
                 'Student ID', 'student_name', 'gender', 'grade', 'reading_score', 'math_score']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_17/target_multisource_mcts.csv", index=False)