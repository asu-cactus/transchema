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

grouped_source0 = source0.groupby('2012-12-05', as_index=False).agg({'301.0':'sum'})

join_01 = pd.merge(grouped_source0, source1, on='2012-12-05', how='outer')
join_02 = pd.merge(join_01, source2, on='2012-12-05', how='outer')
join_03 = pd.merge(join_02, source3, on='2012-12-05', how='outer')
join_04 = pd.merge(join_03, source4, on='2012-12-05', how='outer')
join_05 = pd.merge(join_04, source5, on='2012-12-05', how='outer')
join_06 = pd.merge(join_05, source6, on='2012-12-05', how='outer')
join_07 = pd.merge(join_06, source7, on='2012-12-05', how='outer')
join_08 = pd.merge(join_07, source8, on='2012-12-05', how='outer')
join_09 = pd.merge(join_08, source9, on='2012-12-05', how='outer')
final_df = pd.merge(join_09, source10, on='2012-12-05', how='outer')

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