import pandas as pd

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

# Aggregate df2 by school: average scores and counts of passing students (score >= 70)
df2_agg = df2.groupby('school').agg(
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean'),
    Number_Passing_Math=('math_score', lambda x: (x >= 70).sum()),
    Number_Passing_Reading=('reading_score', lambda x: (x >= 70).sum())
).reset_index()

# Aggregate df0 by school (already aggregated, but keep for join)
df0_agg = df0.copy()

# Join df1 with df0_agg on name=school
merged_1 = pd.merge(df1, df0_agg, left_on='name', right_on='school', how='inner')

# Join merged_1 with df2_agg on name=school
merged_2 = pd.merge(merged_1, df2_agg, left_on='name', right_on='school', how='inner', suffixes=('_df0', '_df2'))

# Use the aggregated values from df2 (student-level) for scores and passing counts, as target examples match these better
# Select and rename columns to match target schema
result = merged_2[[
    'School ID', 'name', 'type', 'size', 'budget',
    'Average_Math_Score', 'Average_Reading_Score',
    'Number_Passing_Math', 'Number_Passing_Reading',
    'size'  # for School Size
]]

result.columns = [
    'School ID', 'name', 'type', 'size', 'budget',
    'Average Math Score', 'Average Reading Score',
    'Number Passing Math', 'Number Passing Reading',
    'School Size'
]

# Group by School ID and name to ensure uniqueness (though join should be one-to-one)
result = result.groupby(['School ID', 'name'], as_index=False).first()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)