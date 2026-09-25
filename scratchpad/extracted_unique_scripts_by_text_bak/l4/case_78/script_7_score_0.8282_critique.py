import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

# Rename columns in source2 to match aggregation target columns
source2_renamed = source2.rename(columns={
    'math_score': 'Average Math Score',
    'reading_score': 'Average Reading Score',
    'school': 'school'
})

# Join source2 (student data) with source1 (school dimension) on school name
joined_s2_s1 = source2_renamed.merge(source1, left_on='school', right_on='name', how='inner')

# Aggregate student-level data grouped by school attributes from source1
agg = joined_s2_s1.groupby(
    ['School ID', 'name', 'type', 'size', 'budget'], as_index=False
).agg({
    'Average Math Score': 'mean',
    'Average Reading Score': 'mean',
    'math_score': 'count',  # not used, just to keep consistent
    'Number Passing Math': 'sum',  # not present in source2, so skip
    'Number Passing Reading': 'sum'  # not present in source2, so skip
})

# Since 'Number Passing Math' and 'Number Passing Reading' are not in source2, we must compute them from source2:
# Number Passing Math: count of students with math_score >= 70
# Number Passing Reading: count of students with reading_score >= 70

# Compute passing counts per school from source2
passing_counts = source2.groupby('school').agg({
    'math_score': lambda x: (x >= 70).sum(),
    'reading_score': lambda x: (x >= 70).sum()
}).rename(columns={
    'math_score': 'Number Passing Math',
    'reading_score': 'Number Passing Reading'
}).reset_index()

# Merge passing counts into agg by school name
agg = agg.merge(passing_counts, left_on='name', right_on='school', how='left')

# Drop redundant 'school' column after merge
agg = agg.drop(columns=['school'])

# Join the aggregated data with source0 (which has school-level aggregates) on school name to get final data
final = agg.merge(source0, left_on='name', right_on='school', how='inner', suffixes=('_agg', '_src0'))

# Construct final DataFrame with target schema columns
result = pd.DataFrame()
result['School ID'] = final['School ID'].astype('Int64')
result['name'] = final['name']
result['type'] = final['type']
result['size'] = final['size'].astype('Int64')
result['budget'] = final['budget'].astype('Int64')

# For average scores, use the aggregated averages from student data (agg)
result['Average Math Score'] = final['Average Math Score'].astype(float)
result['Average Reading Score'] = final['Average Reading Score'].astype(float)

# For number passing, use counts computed from student data (passing_counts)
result['Number Passing Math'] = final['Number Passing Math'].astype('Int64')
result['Number Passing Reading'] = final['Number Passing Reading'].astype('Int64')

# School Size is the same as size from source1
result['School Size'] = final['size'].astype('Int64')

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)