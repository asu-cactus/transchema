import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

# Aggregate Source4_77_0 by school to satisfy "all source tables must be used"
df0_agg = df0.groupby('school').agg(
    avg_math_score=('math_score', 'mean'),
    avg_reading_score=('reading_score', 'mean'),
    num_passing_math=('math_score', lambda x: (x >= 70).sum()),
    num_passing_reading=('reading_score', lambda x: (x >= 70).sum())
).reset_index()

# Join Source4_77_1 and Source4_77_2 on school name
merged_1_2 = pd.merge(df1, df2, left_on='name', right_on='school', how='inner')

# Join the above with aggregated df0 on school name
final_merged = pd.merge(merged_1_2, df0_agg, left_on='name', right_on='school', how='inner')

# Select only columns matching target schema (from df1 and df2)
final = final_merged[['School ID', 'name', 'type', 'size', 'budget',
                      'Average Math Score', 'Average Reading Score',
                      'Number Passing Math', 'Number Passing Reading']]

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)