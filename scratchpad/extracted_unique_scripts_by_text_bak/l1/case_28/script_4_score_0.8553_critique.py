import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_28/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_28/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_28/target_multisource_mcts.csv"

# Read source tables with index_col=0 to ignore the first index column
df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Normalize 'school_name' in both tables for reliable join
df0['school_name_norm'] = df0['school_name'].str.strip().str.lower()
df1['school_name_norm'] = df1['school_name'].str.strip().str.lower()

# Join on normalized school_name
merged = pd.merge(df1, df0, left_on='school_name_norm', right_on='school_name_norm', how='inner')

# Drop the normalized join key columns
merged = merged.drop(columns=['school_name_norm'])

# Select columns in the exact order of target schema
merged = merged[['Student ID', 'student_name', 'gender', 'grade', 'school_name_x', 'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']]

# Rename 'school_name_x' back to 'school_name' to match target schema
merged = merged.rename(columns={'school_name_x': 'school_name'})

# Cast columns to correct types
merged = merged.astype({
    'Student ID': int,
    'reading_score': int,
    'math_score': int,
    'School ID': int,
    'size': int,
    'budget': int
})

# Write to target CSV without index
merged.to_csv(target_path, index=False)