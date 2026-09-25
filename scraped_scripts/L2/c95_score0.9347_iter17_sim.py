import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_95/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_95/training_1.csv", index_col=0)

agg = source1.groupby(['grade', 'school']).agg(
    School_Size=('Student ID', 'count'),
    Average_Student_Math_Score=('math_score', 'mean'),
    Student_Reading_Score=('reading_score', 'min'),
    Student_Reading_Score_MaxMath=('math_score', 'max')  # temp column, will discard later
).reset_index()

# Join on school name
joined = pd.merge(source0, agg, left_on='name', right_on='school', how='inner')

# Construct final columns and rename
result = pd.DataFrame()
result['School Name'] = joined['name']
result['Student Grade'] = joined['grade']
result['School ID'] = joined['School ID'].astype('Int64')
result['School Size'] = joined['size'].astype('Int64')
result['School Budget'] = joined['budget'].astype('Int64')
result['Student ID'] = joined['School_Size'].astype(float)  # COUNT(Student ID) as float
result['Student Reading Score'] = joined['Student_Reading_Score'].astype(float)
result['Average Student Math Score'] = joined['Average_Student_Math_Score'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_95/target_multisource_mcts.csv", index=False)