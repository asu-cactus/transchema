import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_28/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_28/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, on="school_name", how="left")

merged = merged.rename(columns={"Student ID": "Student ID", "student_name": "student_name", "gender": "gender",
                                "grade": "grade", "school_name": "school_name", "reading_score": "reading_score",
                                "math_score": "math_score", "School ID": "School ID", "type": "type",
                                "size": "size", "budget": "budget"})

merged = merged[['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score',
                 'School ID', 'type', 'size', 'budget']]

merged['Student ID'] = merged['Student ID'].astype('Int64')
merged['reading_score'] = merged['reading_score'].astype('Int64')
merged['math_score'] = merged['math_score'].astype('Int64')
merged['School ID'] = merged['School ID'].astype('Int64')
merged['size'] = merged['size'].astype('Int64')
merged['budget'] = merged['budget'].astype('Int64')

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_28/target_multisource_mcts.csv", index=False)