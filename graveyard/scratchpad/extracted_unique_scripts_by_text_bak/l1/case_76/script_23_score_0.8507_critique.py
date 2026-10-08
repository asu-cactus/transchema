import pandas as pd

# Read source files with index_col=0 to ignore the first index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_1.csv", index_col=0)

# Clean 'school_name' columns by stripping whitespace to ensure proper join
df0['school_name'] = df0['school_name'].str.strip()
df1['school_name'] = df1['school_name'].str.strip()

# Perform inner join on 'school_name'
merged = pd.merge(df0, df1, on='school_name', how='inner')

# Select columns in the order of the target schema
merged = merged[['Student ID', 'student_name', 'gender', 'grade', 'school_name',
                 'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']]

# Ensure correct data types as per target schema
merged = merged.astype({
    'Student ID': int,
    'student_name': str,
    'gender': str,
    'grade': str,
    'school_name': str,
    'reading_score': int,
    'math_score': int,
    'School ID': int,
    'type': str,
    'size': int,
    'budget': int
})

# Write output CSV without index
merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_76/target_multisource_mcts.csv", index=False)