import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_32/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_32/training_1.csv", index_col=0)

# Join student data with school data on school_name
merged = pd.merge(source1, source0, on="school_name", how="left")

# Select columns in the exact order and names as target schema
cols = ['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score',
        'School ID', 'type', 'size', 'budget']
result = merged[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_32/target_multisource_mcts.csv", index=False)