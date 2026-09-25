import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="school_name", how="left")

merged = merged.rename(columns={"School ID": "School ID"})

cols = ['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score',
        'School ID', 'type', 'size', 'budget']

result = merged[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_76/target_multisource_mcts.csv", index=False)