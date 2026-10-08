import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_95/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_95/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_95/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_95/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# GROUP BY Subject and count rows for each other column
agg_df = df.groupby('Subject', as_index=False).agg({
    'SubjectId': 'count',
    'Split': 'count',
    'PA': 'count',
    'AB': 'count',
    'H': 'count',
    'TB': 'count',
    'BB': 'count',
    'SF': 'count',
    'HBP': 'count'
})

# Rename columns to match target schema exactly
agg_df.columns = ['Subject', 'SubjectId', 'Split', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']

# Convert types to match target schema
agg_df['SubjectId'] = agg_df['SubjectId'].astype(int)
agg_df['Split'] = agg_df['Split'].astype(int)
agg_df['PA'] = agg_df['PA'].astype(int)
agg_df['AB'] = agg_df['AB'].astype(int)
agg_df['H'] = agg_df['H'].astype(int)
agg_df['TB'] = agg_df['TB'].astype(int)
agg_df['BB'] = agg_df['BB'].astype(int)
agg_df['SF'] = agg_df['SF'].astype(int)
agg_df['HBP'] = agg_df['HBP'].astype(int)

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_95/target_multisource_mcts.csv", index=False)