import pandas as pd

src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_17/test_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_17/test_1.csv', index_col=0)

merged = pd.merge(
    src0,
    src1,
    on='school_name',
    how='left',
    suffixes=('', '_drop'),
).reindex(columns=[
    'School ID', 'school_name', 'type', 'size', 'budget', 
    'Student ID', 'student_name', 'gender', 'grade', 
    'reading_score', 'math_score'
])

merged.to_csv('autopipeline-benchmarks/github-pipelines/length1_17/target_multisource_mcts_recovery_test_val.csv')