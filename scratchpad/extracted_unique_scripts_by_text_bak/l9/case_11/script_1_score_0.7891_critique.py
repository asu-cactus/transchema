import pandas as pd

# Read all source tables
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_9.csv", index_col=0)

# Rename columns to match target schema except the key column '2012-12-05'
source0.columns = ['2012-12-05', '0.7268']
source1.columns = ['2012-12-05', '0.016157143']
source2.columns = ['2012-12-05', '0.17657143']
source3.columns = ['2012-12-05', '6.9']
source4.columns = ['2012-12-05', '0.0075805085']
source5.columns = ['2012-12-05', '0.0179']
source6.columns = ['2012-12-05', '242.364']
source7.columns = ['2012-12-05', '301.0']
source8.columns = ['2012-12-05', '20.3333']
source9.columns = ['2012-12-05', '0.1646']

# Join all sources on '2012-12-05' using inner join to keep only matching dates
df = source0.merge(source1, on='2012-12-05', how='inner') \
            .merge(source2, on='2012-12-05', how='inner') \
            .merge(source3, on='2012-12-05', how='inner') \
            .merge(source4, on='2012-12-05', how='inner') \
            .merge(source5, on='2012-12-05', how='inner') \
            .merge(source6, on='2012-12-05', how='inner') \
            .merge(source7, on='2012-12-05', how='inner') \
            .merge(source8, on='2012-12-05', how='inner') \
            .merge(source9, on='2012-12-05', how='inner')

# Convert data types to match target schema
df['2012-12-05'] = df['2012-12-05'].astype(str)
df['301.0'] = df['301.0'].astype('Int64')  # nullable integer type
df['0.0075805085'] = df['0.0075805085'].astype(float)
df['0.0179'] = df['0.0179'].astype(float)
df['6.9'] = df['6.9'].astype(float)
df['0.17657143'] = df['0.17657143'].astype(float)
df['20.3333'] = df['20.3333'].astype(float)
df['0.016157143'] = df['0.016157143'].astype(float)
df['242.364'] = df['242.364'].astype(float)
df['0.1646'] = df['0.1646'].astype(float)
df['0.7268'] = df['0.7268'].astype(float)

# Write to output CSV
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_11/target_multisource_mcts.csv", index=False)