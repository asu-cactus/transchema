import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length5_30/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length5_30/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length5_30/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on school_name
merged = pd.merge(df1, df0[['school_name', 'budget']], on='school_name', how='inner')

# Group by school_name and aggregate
agg_df = merged.groupby('school_name').agg(
    **{
        'Student ID': ('Student ID', 'count'),
        'budget': ('budget', 'sum'),
        'math_score': ('math_score', 'mean'),
        'reading_score': ('reading_score', 'mean')
    }
).reset_index()

# Ensure correct dtypes
agg_df['school_name'] = agg_df['school_name'].astype(str)
agg_df['Student ID'] = agg_df['Student ID'].astype(int)
agg_df['budget'] = agg_df['budget'].astype(int)
agg_df['math_score'] = agg_df['math_score'].astype(float)
agg_df['reading_score'] = agg_df['reading_score'].astype(float)

agg_df.to_csv(output_path, index=False)