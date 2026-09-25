import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_17/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_17/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_17/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(df0, df1, how='inner', left_on='school_name', right_on='school_name')

result = merged[['School ID', 'school_name', 'type', 'size', 'budget',
                 'Student ID', 'student_name', 'gender', 'grade', 'reading_score', 'math_score']]

result.to_csv(target_path, index=False)