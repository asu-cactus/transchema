import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_32/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_32/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, on="school_name", how="left")

merged = merged.rename(columns={"Student ID": "Student ID", "student_name": "student_name", "gender": "gender",
                                "grade": "grade", "school_name": "school_name", "reading_score": "reading_score",
                                "math_score": "math_score", "School ID": "School ID", "type": "type",
                                "size": "size", "budget": "budget"})

cols = ['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score',
        'School ID', 'type', 'size', 'budget']
result = merged[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_32/target_multisource_mcts.csv", index=False)