import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

# Aggregate Source0 to get counts of passing students per school
# Define passing threshold as 70 for both math and reading (typical assumption)
passing_math = source0['math_score'] >= 70
passing_reading = source0['reading_score'] >= 70

agg_source0 = source0.groupby('school').agg(
    Number_Passing_Math=('math_score', lambda x: passing_math.loc[x.index].sum()),
    Number_Passing_Reading=('reading_score', lambda x: passing_reading.loc[x.index].sum())
).reset_index()

# Join Source1 and Source2 on school name
join_1_2 = pd.merge(source1, source2, left_on='name', right_on='school', how='inner')

# Join the above with aggregated Source0 counts on school name
final_join = pd.merge(join_1_2, agg_source0, left_on='name', right_on='school', how='inner')

# Now prepare final dataframe with correct columns and aggregation
# Group by School ID and name (leftmost unique keys)
grouped = final_join.groupby(['School ID', 'name'], as_index=False).agg({
    'type': 'first',
    'size': 'first',
    'budget': 'first',
    'Average Math Score': 'first',
    'Average Reading Score': 'first',
    'Number_Passing_Math': 'sum',
    'Number_Passing_Reading': 'sum'
})

# Rename columns to match target schema exactly
grouped = grouped.rename(columns={
    'Number_Passing_Math': 'Number Passing Math',
    'Number_Passing_Reading': 'Number Passing Reading'
})

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)