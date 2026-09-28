import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_28/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_28/training_1.csv", index_col=0)

# Join Source1 (students) with Source0 (schools) on school_name
merged = pd.merge(source1, source0, on="school_name", how="left")

# Select and order columns exactly as in target schema
merged = merged[['Student ID', 'student_name', 'gender', 'grade', 'school_name',
                 'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']]

# Cast columns to correct types as per target schema
merged['Student ID'] = merged['Student ID'].astype('Int64')
merged['reading_score'] = merged['reading_score'].astype('Int64')
merged['math_score'] = merged['math_score'].astype('Int64')
merged['School ID'] = merged['School ID'].astype('Int64')
merged['size'] = merged['size'].astype('Int64')
merged['budget'] = merged['budget'].astype('Int64')

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_28/target_multisource_mcts.csv", index=False)