import pandas as pd

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

# Join all sources on '2012-12-05' using inner join to keep only matching keys
joined_01 = pd.merge(source0, source1, on='2012-12-05', how='inner')
joined_02 = pd.merge(joined_01, source2, on='2012-12-05', how='inner')
joined_03 = pd.merge(joined_02, source3, on='2012-12-05', how='inner')
joined_04 = pd.merge(joined_03, source4, on='2012-12-05', how='inner')
joined_05 = pd.merge(joined_04, source5, on='2012-12-05', how='inner')
joined_06 = pd.merge(joined_05, source6, on='2012-12-05', how='inner')
joined_07 = pd.merge(joined_06, source7, on='2012-12-05', how='inner')
joined_08 = pd.merge(joined_07, source8, on='2012-12-05', how='inner')
joined_09 = pd.merge(joined_08, source9, on='2012-12-05', how='inner')
final_df = pd.merge(joined_09, source10, on='2012-12-05', how='inner')

# Cast columns to correct types as per target schema
final_df = final_df.astype({
    '2012-12-05': str,
    '301.0': 'Int64',
    '0.0075805085': 'float',
    '0.0179': 'float',
    '6.9': 'float',
    '0.17657143': 'float',
    '20.3333': 'float',
    '0.016157143': 'float',
    '242.364': 'float',
    '0.1646': 'float',
    '0.7268': 'float',
    '0.4332': 'float'
})

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_12/target_multisource_mcts.csv", index=False)