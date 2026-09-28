import pandas as pd

# Read all source files with index_col=0 to ignore the first numerical index column
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_9.csv", index_col=0)
source10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_10.csv", index_col=0)

# Merge all sources on '2012-12-05' using outer join to keep all dates
df = pd.merge(source0, source1, on='2012-12-05', how='outer')
df = pd.merge(df, source2, on='2012-12-05', how='outer')
df = pd.merge(df, source3, on='2012-12-05', how='outer')
df = pd.merge(df, source4, on='2012-12-05', how='outer')
df = pd.merge(df, source5, on='2012-12-05', how='outer')
df = pd.merge(df, source6, on='2012-12-05', how='outer')
df = pd.merge(df, source7, on='2012-12-05', how='outer')
df = pd.merge(df, source8, on='2012-12-05', how='outer')
df = pd.merge(df, source9, on='2012-12-05', how='outer')
df = pd.merge(df, source10, on='2012-12-05', how='outer')

# Convert columns to correct types according to target schema
# '301.0' is integer, others are float
df['301.0'] = pd.to_numeric(df['301.0'], errors='coerce').astype('Int64')

float_columns = ['0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333',
                 '0.016157143', '242.364', '0.1646', '0.7268', '0.4332']

for col in float_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)

# Reorder columns exactly as target schema
df = df[['2012-12-05', '301.0', '0.0075805085', '0.0179', '6.9', '0.17657143',
         '20.3333', '0.016157143', '242.364', '0.1646', '0.7268', '0.4332']]

# Write to target file
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_12/target_multisource_mcts.csv", index=False)