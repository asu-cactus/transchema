import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

# Create pass indicators in source2
pass_math = (source2['math_score'] >= 60).astype(int)
pass_reading = (source2['reading_score'] >= 60).astype(int)

# Aggregate source2 by school
agg_source2 = source2.groupby('school').agg(
    **{
        'Average Math Score': ('math_score', 'mean'),
        'Average Reading Score': ('reading_score', 'mean'),
        'Number Passing Math': (pass_math, 'sum'),
        'Number Passing Reading': (pass_reading, 'sum')
    }
).reset_index()

# Join source1 and source0 on school name
join_1_0 = pd.merge(source1, source0, left_on='name', right_on='school', how='inner')

# Join the above with aggregated source2 on school name
join_all = pd.merge(join_1_0, agg_source2, left_on='name', right_on='school', how='inner')

# Select and rename columns to match target schema
result = join_all[[
    'School ID', 'name', 'type', 'size', 'budget',
    'Average Math Score_y', 'Average Reading Score_y',
    'Number Passing Math_y', 'Number Passing Reading_y', 'size'
]].rename(columns={
    'Average Math Score_y': 'Average Math Score',
    'Average Reading Score_y': 'Average Reading Score',
    'Number Passing Math_y': 'Number Passing Math',
    'Number Passing Reading_y': 'Number Passing Reading',
    'size': 'School Size'
})

# Group by School ID and name to ensure uniqueness (should be unique already)
result = result.groupby(['School ID', 'name'], as_index=False).agg({
    'type': 'first',
    'size': 'first',
    'budget': 'first',
    'Average Math Score': 'mean',
    'Average Reading Score': 'mean',
    'Number Passing Math': 'sum',
    'Number Passing Reading': 'sum',
    'School Size': 'first'
})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)