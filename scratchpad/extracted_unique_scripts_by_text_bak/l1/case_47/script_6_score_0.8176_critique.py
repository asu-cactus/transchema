import pandas as pd

# Read source tables with index_col=0 as instructed
df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_47/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_47/training_1.csv", index_col=0)

# Normalize 'school_name' in both tables to ensure exact matching (strip whitespace)
df_students['school_name'] = df_students['school_name'].str.strip()
df_schools['school_name'] = df_schools['school_name'].str.strip()

# Join on 'school_name' (inner join)
df = pd.merge(df_students, df_schools, on='school_name', how='inner')

# Select and reorder columns exactly as target schema
df = df[['Student ID', 'student_name', 'gender', 'grade', 'school_name',
         'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']]

# Cast columns to correct types as per target schema
df['Student ID'] = df['Student ID'].astype(int)
df['reading_score'] = df['reading_score'].astype(int)
df['math_score'] = df['math_score'].astype(int)
df['School ID'] = df['School ID'].astype(int)
df['size'] = df['size'].astype(int)
df['budget'] = df['budget'].astype(int)

# Write output CSV without index
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_47/target_multisource_mcts.csv", index=False)