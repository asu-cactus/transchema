import pandas as pd

# Read all source CSVs with index_col=0 as instructed
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert 'Split' and 'Subject' to categorical codes (integers)
df_all['Split'] = df_all['Split'].astype('category').cat.codes
df_all['Subject'] = df_all['Subject'].astype('category').cat.codes

# Group by the composite key and sum the numeric columns
agg_df = df_all.groupby(['SubjectId', 'Split', 'Subject'], as_index=False).agg({
    'PA': 'sum',
    'AB': 'sum',
    'H': 'sum',
    'TB': 'sum',
    'BB': 'sum',
    'SF': 'sum',
    'HBP': 'sum'
})

# Ensure all columns have correct types as per target schema
agg_df['SubjectId'] = agg_df['SubjectId'].astype(int)
agg_df['Split'] = agg_df['Split'].astype(int)
agg_df['Subject'] = agg_df['Subject'].astype(int)
agg_df['PA'] = agg_df['PA'].astype(int)
agg_df['AB'] = agg_df['AB'].astype(int)
agg_df['H'] = agg_df['H'].astype(int)
agg_df['TB'] = agg_df['TB'].astype(int)
agg_df['BB'] = agg_df['BB'].astype(int)
agg_df['SF'] = agg_df['SF'].astype(int)
agg_df['HBP'] = agg_df['HBP'].astype(int)

# Reorder columns to match target schema exactly
agg_df = agg_df[['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

# Write output CSV
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)