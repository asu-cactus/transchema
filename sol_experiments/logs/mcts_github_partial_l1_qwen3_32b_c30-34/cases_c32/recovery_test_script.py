import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_32/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_32/test_1.csv', index_col=0)

merged = df1.merge(df0, how='left', left_on='school_name', right_on='school_name')

merged[
    ['Student ID', 'student_name', 'gender', 'grade', 'school_name', 
     'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']
].to_csv(
    'autopipeline-benchmarks/github-pipelines/length1_32/target_multisource_mcts_recovery_test_val.csv', 
    index=False
)