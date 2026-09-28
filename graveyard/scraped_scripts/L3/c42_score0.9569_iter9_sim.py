import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_42/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_42/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length3_42/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

pivot = df1.pivot_table(index='school_name', columns='grade', values=['math_score', 'reading_score'], aggfunc='mean')
pivot.columns = ['_'.join(col).replace('math_score', 'mean_math_score').replace('reading_score', 'mean_reading_score') for col in pivot.columns]
pivot.reset_index(inplace=True)

joined = pd.merge(pivot, df0, on='school_name', how='inner')

grouped = joined.groupby('size').agg(
    **{
        'School Size': ('size', 'sum'),
        'Total Students': ('size', 'sum'),
        'Total School Budget': ('budget', 'sum'),
        'Average Math Score': ('mean_math_score_9th', 'mean'),
        'Average Reading Score': ('mean_reading_score_9th', 'mean'),
    }
).reset_index(drop=True)

# The target examples show Average Math/Reading Score as overall averages, not per grade.
# So we need to compute average math and reading scores across all grades per school, then average per size group.

# Instead of using only 9th grade columns, compute average math and reading scores per school first:
math_cols = [c for c in pivot.columns if c.startswith('mean_math_score_')]
reading_cols = [c for c in pivot.columns if c.startswith('mean_reading_score_')]

joined['Average Math Score'] = joined[math_cols].mean(axis=1)
joined['Average Reading Score'] = joined[reading_cols].mean(axis=1)

grouped = joined.groupby('size').agg(
    **{
        'School Size': ('size', 'sum'),
        'Total Students': ('size', 'sum'),
        'Total School Budget': ('budget', 'sum'),
        'Average Math Score': ('Average Math Score', 'mean'),
        'Average Reading Score': ('Average Reading Score', 'mean'),
    }
).reset_index(drop=True)

grouped = grouped.rename(columns={'School Size': 'School Size',
                                  'Total Students': 'Total Students',
                                  'Total School Budget': 'Total School Budget',
                                  'Average Math Score': 'Average Math Score',
                                  'Average Reading Score': 'Average Reading Score'})

grouped = grouped.astype({
    'School Size': 'int64',
    'Total Students': 'int64',
    'Total School Budget': 'int64',
    'Average Math Score': 'float64',
    'Average Reading Score': 'float64'
})

grouped.to_csv(output_path, index=False)