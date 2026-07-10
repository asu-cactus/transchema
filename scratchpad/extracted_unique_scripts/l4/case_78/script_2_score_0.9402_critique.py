import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)  # Not used in final aggregation
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

# Compute passing counts in df2
# Passing means score >= 60 (common passing threshold)
df2['Number Passing Math'] = (df2['math_score'] >= 60).astype(int)
df2['Number Passing Reading'] = (df2['reading_score'] >= 60).astype(int)

# Aggregate student scores by school
agg_scores = df2.groupby('school', as_index=False).agg({
    'math_score': 'mean',
    'reading_score': 'mean',
    'Number Passing Math': 'sum',
    'Number Passing Reading': 'sum'
})

# Rename columns to match target schema
agg_scores = agg_scores.rename(columns={
    'school': 'name',
    'math_score': 'Average Math Score',
    'reading_score': 'Average Reading Score'
})

# Join aggregated scores with school info from df1 on name
merged = pd.merge(df1, agg_scores, on='name', how='inner')

# Add School Size column same as size
merged['School Size'] = merged['size']

# Select and reorder columns to match target schema exactly
final_cols = ['School ID', 'name', 'type', 'size', 'budget',
              'Average Math Score', 'Average Reading Score',
              'Number Passing Math', 'Number Passing Reading', 'School Size']

final_df = merged[final_cols]

# Group by leftmost columns to ensure uniqueness (should be unique already)
final_df = final_df.groupby(['School ID', 'name', 'type', 'size', 'budget'], as_index=False).agg({
    'Average Math Score': 'mean',
    'Average Reading Score': 'mean',
    'Number Passing Math': 'sum',
    'Number Passing Reading': 'sum',
    'School Size': 'first'  # School Size same as size, so first is fine
})

# Ensure correct dtypes
final_df = final_df.astype({
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
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)