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

# Join all tables on '2012-12-05' using inner joins to keep only matching keys
joined = s7.merge(s0, on='2012-12-05', how='inner') \
           .merge(s1, on='2012-12-05', how='inner') \
           .merge(s2, on='2012-12-05', how='inner') \
           .merge(s3, on='2012-12-05', how='inner') \
           .merge(s4, on='2012-12-05', how='inner') \
           .merge(s5, on='2012-12-05', how='inner') \
           .merge(s6, on='2012-12-05', how='inner') \
           .merge(s8, on='2012-12-05', how='inner') \
           .merge(s9, on='2012-12-05', how='inner')

# Select columns exactly as in target schema
result = joined[['2012-12-05', '301.0', '0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268']]

# Cast columns to correct types
result['2012-12-05'] = result['2012-12-05'].astype(str)
result['301.0'] = result['301.0'].astype('Int64')
result['0.0075805085'] = result['0.0075805085'].astype(float)
result['0.0179'] = result['0.0179'].astype(float)
result['6.9'] = result['6.9'].astype(float)
result['0.17657143'] = result['0.17657143'].astype(float)
result['20.3333'] = result['20.3333'].astype(float)
result['0.016157143'] = result['0.016157143'].astype(float)
result['242.364'] = result['242.364'].astype(float)
result['0.1646'] = result['0.1646'].astype(float)
result['0.7268'] = result['0.7268'].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_11/target_multisource_mcts.csv", index=False)