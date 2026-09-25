import pandas as pd

# Read source tables with index_col=0 as per hint 22
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_62/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_62/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_62/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_62/training_3.csv', index_col=0)

# Join source0 and source1 on key columns
joined_01 = pd.merge(
    source0, source1,
    on=['student_num', 'lea_avg_student_num', 'st_avg_student_num', 'year'],
    how='inner',
    suffixes=('', '_s1')
)

# Join the result with source2
joined_012 = pd.merge(
    joined_01, source2,
    on=['student_num', 'lea_avg_student_num', 'st_avg_student_num', 'year'],
    how='inner',
    suffixes=('', '_s2')
)

# Join the result with source3
final_df = pd.merge(
    joined_012, source3,
    on=['student_num', 'lea_avg_student_num', 'st_avg_student_num', 'year'],
    how='inner',
    suffixes=('', '_s3')
)

# The target schema expects columns without suffixes, so keep original columns from source0,
# and columns from other sources with suffixes as is (since target schema has all columns combined).
# No aggregation or group by needed as keys are unique.

# Write final output to the specified path
final_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_62/target_multisource_mcts.csv', index=False)