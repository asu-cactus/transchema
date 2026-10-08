import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

# Aggregate Source0 to get counts of passing students per school
# Define passing as score >= 70 (common passing threshold)
passing_math = source0[source0['math_score'] >= 70].groupby('school').size().rename('Number Passing Math')
passing_reading = source0[source0['reading_score'] >= 70].groupby('school').size().rename('Number Passing Reading')

# Combine passing counts into one DataFrame
passing_counts = pd.concat([passing_math, passing_reading], axis=1).reset_index()

# Join Source1 (school dimension) with Source2 (average scores) on school name
school_scores = source1.merge(source2, left_on='name', right_on='school', how='inner')

# Join the above with passing counts from Source0 on school name
full = school_scores.merge(passing_counts, left_on='name', right_on='school', how='inner')

# Select and reorder columns to match target schema
result = full[['School ID', 'name', 'type', 'size', 'budget',
               'Average Math Score', 'Average Reading Score',
               'Number Passing Math', 'Number Passing Reading']]

# Cast columns to target types
result['School ID'] = result['School ID'].astype(int)
result['size'] = result['size'].astype(int)
result['budget'] = result['budget'].astype(int)
result['Number Passing Math'] = result['Number Passing Math'].astype(int)
result['Number Passing Reading'] = result['Number Passing Reading'].astype(int)
result['Average Math Score'] = result['Average Math Score'].astype(float)
result['Average Reading Score'] = result['Average Reading Score'].astype(float)
result['name'] = result['name'].astype(str)
result['type'] = result['type'].astype(str)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)