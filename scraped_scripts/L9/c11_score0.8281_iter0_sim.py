import pandas as pd

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

grouped = s7.groupby('2012-12-05', as_index=False).agg({'301.0':'sum'})

joined_0 = pd.merge(grouped, s0, on='2012-12-05', how='left')
joined_1 = pd.merge(joined_0, s1, on='2012-12-05', how='left')
joined_2 = pd.merge(joined_1, s2, on='2012-12-05', how='left')
joined_3 = pd.merge(joined_2, s3, on='2012-12-05', how='left')
joined_4 = pd.merge(joined_3, s4, on='2012-12-05', how='left')
joined_5 = pd.merge(joined_4, s5, on='2012-12-05', how='left')
joined_6 = pd.merge(joined_5, s6, on='2012-12-05', how='left')
joined_7 = pd.merge(joined_6, s8, on='2012-12-05', how='left')
joined_8 = pd.merge(joined_7, s9, on='2012-12-05', how='left')

result = joined_8[['2012-12-05', '301.0', '0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268']]

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

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_11/target_multisource_mcts.csv", index=False)