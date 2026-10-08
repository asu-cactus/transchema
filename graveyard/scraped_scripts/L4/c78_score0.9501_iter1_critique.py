import pandas as pd

# Read source files
df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv', index_col=0)

# Aggregate student-level data (Source4_78_2) by school
df2_agg = df2.groupby('school', as_index=False).agg({
    'math_score': 'mean',
    'reading_score': 'mean',
    'Student ID': 'count'  # count of students, not used directly but can be ignored
}).rename(columns={
    'math_score': 'Average Math Score',
    'reading_score': 'Average Reading Score'
})

# Calculate Number Passing Math and Number Passing Reading from student-level data
# Passing means score >= 60 (assuming passing threshold, but since no threshold given, 
# we must derive counts from source0 or assume counts from source2)
# Since source0 already has Number Passing Math/Reading, and target examples match source0 counts,
# we will trust source0 counts and not recalc passing counts from source2.

# Join aggregated student scores with source0 on school
df0_renamed = df0.rename(columns={'school': 'school'})
merged_scores = pd.merge(df0_renamed, df2_agg, on='school', how='inner', suffixes=('_source0', '_source2'))

# For Average Math/Reading Score, take mean of the two averages (unweighted mean)
merged_scores['Average Math Score'] = merged_scores[['Average Math Score_source0', 'Average Math Score_source2']].mean(axis=1)
merged_scores['Average Reading Score'] = merged_scores[['Average Reading Score_source0', 'Average Reading Score_source2']].mean(axis=1)

# Keep Number Passing Math and Number Passing Reading from source0 (since source2 does not have passing counts)
merged_scores = merged_scores[['school', 'Average Math Score', 'Average Reading Score', 'Number Passing Math', 'Number Passing Reading']]

# Join with source1 on school name = name
final_merged = pd.merge(merged_scores, df1, left_on='school', right_on='name', how='inner')

# Group by primary key columns of target and aggregate numeric columns
result = final_merged.groupby(['School ID', 'name', 'type', 'size', 'budget'], as_index=False).agg({
    'Average Math Score': 'mean',
    'Average Reading Score': 'mean',
    'Number Passing Math': 'sum',
    'Number Passing Reading': 'sum'
})

# Add School Size column as a copy of size
result['School Size'] = result['size']

# Cast columns to target types
result = result.astype({
    'School ID': 'int64',
    'name': 'string',
    'type': 'string',
    'size': 'int64',
    'budget': 'int64',
    'Average Math Score': 'float64',
    'Average Reading Score': 'float64',
    'Number Passing Math': 'int64',
    'Number Passing Reading': 'int64',
    'School Size': 'int64'
})

# Write output
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv', index=False)