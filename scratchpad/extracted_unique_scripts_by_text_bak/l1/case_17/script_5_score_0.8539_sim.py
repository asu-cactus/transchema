import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_17/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_17/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, how="inner", on="school_name")

merged = merged[['School ID', 'school_name', 'type', 'size', 'budget', 'Student ID', 'student_name', 'gender', 'grade', 'reading_score', 'math_score']]

merged['School ID'] = merged['School ID'].astype('Int64')
merged['size'] = merged['size'].astype('Int64')
merged['budget'] = merged['budget'].astype('Int64')
merged['Student ID'] = merged['Student ID'].astype('Int64')
merged['reading_score'] = merged['reading_score'].astype('Int64')
merged['math_score'] = merged['math_score'].astype('Int64')

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_17/target_multisource_mcts.csv", index=False)