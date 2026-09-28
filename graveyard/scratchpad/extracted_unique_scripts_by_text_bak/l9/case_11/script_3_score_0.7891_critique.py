import pandas as pd

# Read sources with index_col=0 to ignore the numerical index column
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

# Rename the value columns to match the target schema columns
# Target schema columns (excluding date): ['301.0', '0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268']
# Source tables have columns: ['2012-12-05', <value_column>]
# We map each source's value column to the corresponding target column name:

s0.columns = ['2012-12-05', '0.7268']
s1.columns = ['2012-12-05', '0.016157143']
s2.columns = ['2012-12-05', '0.17657143']
s3.columns = ['2012-12-05', '6.9']
s4.columns = ['2012-12-05', '0.0075805085']
s5.columns = ['2012-12-05', '0.0179']
s6.columns = ['2012-12-05', '242.364']
s7.columns = ['2012-12-05', '301.0']
s8.columns = ['2012-12-05', '20.3333']
s9.columns = ['2012-12-05', '0.1646']

# Merge all sources on '2012-12-05' using inner join
df = s0.merge(s1, on='2012-12-05', how='inner')
df = df.merge(s2, on='2012-12-05', how='inner')
df = df.merge(s3, on='2012-12-05', how='inner')
df = df.merge(s4, on='2012-12-05', how='inner')
df = df.merge(s5, on='2012-12-05', how='inner')
df = df.merge(s6, on='2012-12-05', how='inner')
df = df.merge(s7, on='2012-12-05', how='inner')
df = df.merge(s8, on='2012-12-05', how='inner')
df = df.merge(s9, on='2012-12-05', how='inner')

# Convert '301.0' column to integer type as in target schema
df['301.0'] = df['301.0'].astype('Int64')

# Reorder columns to match target schema exactly
target_columns = ['2012-12-05', '301.0', '0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268']
df = df[target_columns]

# Write to output CSV without index
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_11/target_multisource_mcts.csv", index=False)