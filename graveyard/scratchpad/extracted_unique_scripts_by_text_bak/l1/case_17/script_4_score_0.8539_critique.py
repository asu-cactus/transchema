import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_17/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_17/training_1.csv", index_col=0)

# Join on school_name to combine school info with student info
merged = pd.merge(source0, source1, on="school_name", how="inner")

# Reorder columns to match target schema exactly
result = merged[['School ID', 'school_name', 'type', 'size', 'budget',
                 'Student ID', 'student_name', 'gender', 'grade', 'reading_score', 'math_score']]

# Cast columns to correct types as per target schema
result['School ID'] = result['School ID'].astype('Int64')
result['size'] = result['size'].astype('Int64')
result['budget'] = result['budget'].astype('Int64')
result['Student ID'] = result['Student ID'].astype('Int64')
result['reading_score'] = result['reading_score'].astype('Int64')
result['math_score'] = result['math_score'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_17/target_multisource_mcts.csv", index=False)