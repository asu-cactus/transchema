import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_17/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_17/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, on="school_name", how="inner")

result = merged.rename(columns={"Student ID": "Student ID", "student_name": "student_name", "gender": "gender", "grade": "grade",
                                "reading_score": "reading_score", "math_score": "math_score",
                                "School ID": "School ID", "school_name": "school_name", "type": "type", "size": "size", "budget": "budget"})

result = result[['School ID', 'school_name', 'type', 'size', 'budget', 'Student ID', 'student_name', 'gender', 'grade', 'reading_score', 'math_score']]

result['School ID'] = result['School ID'].astype('Int64')
result['size'] = result['size'].astype('Int64')
result['budget'] = result['budget'].astype('Int64')
result['Student ID'] = result['Student ID'].astype('Int64')
result['reading_score'] = result['reading_score'].astype('Int64')
result['math_score'] = result['math_score'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_17/target_multisource_mcts.csv", index=False)