import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_9.csv", index_col=0)

# Merge all tables on '2012-12-05' using inner join to keep only matching keys
df = s7.merge(s4, on='2012-12-05', how='inner')
df = df.merge(s5, on='2012-12-05', how='inner')
df = df.merge(s3, on='2012-12-05', how='inner')
df = df.merge(s2, on='2012-12-05', how='inner')
df = df.merge(s1, on='2012-12-05', how='inner')
df = df.merge(s0, on='2012-12-05', how='inner')
df = df.merge(s8, on='2012-12-05', how='inner')
df = df.merge(s9, on='2012-12-05', how='inner')
df = df.merge(s6, on='2012-12-05', how='inner')

# Convert columns to correct types
df['2012-12-05'] = df['2012-12-05'].astype(str)
df['301.0'] = pd.to_numeric(df['301.0'], errors='coerce').astype('Int64')
for col in ['0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268']:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)

# Group by '2012-12-05' and aggregate
agg_dict = {
    '301.0': 'sum',
    '0.0075805085': 'mean',
    '0.0179': 'mean',
    '6.9': 'mean',
    '0.17657143': 'mean',
    '20.3333': 'mean',
    '0.016157143': 'mean',
    '242.364': 'mean',
    '0.1646': 'mean',
    '0.7268': 'mean'
}

df = df.groupby('2012-12-05', as_index=False).agg(agg_dict)

# Ensure '301.0' is integer type after aggregation
df['301.0'] = df['301.0'].astype('Int64')

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_11/target_multisource_mcts.csv", index=False)