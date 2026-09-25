import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

grouped_source2 = source2.groupby('Institution', as_index=False).mean()

joined_0 = pd.merge(grouped_source2, source1, on='Institution', how='inner')
joined_1 = pd.merge(joined_0, source3, on='Institution', how='inner')
joined_2 = pd.merge(joined_1, source0, on='Institution', how='inner')
final_df = pd.merge(joined_2, source4, on='Institution', how='inner')

final_df = final_df.rename(columns={
    'year 2014': 'persist 2014',
    'year 2015': 'persist 2015',
    'year 2016': 'persist 2016'
})

final_df = final_df[['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
                     'persist 2014', 'persist 2015', 'persist 2016',
                     'Cohort 2014', 'Cohort 2015', 'Cohort 2016']]

final_df['persist 2014'] = final_df['persist 2014'].astype('Int64')
final_df['persist 2015'] = final_df['persist 2015'].astype('Int64')
final_df['persist 2016'] = final_df['persist 2016'].astype('Int64')
final_df['Cohort 2014'] = final_df['Cohort 2014'].astype('Int64')
final_df['Cohort 2015'] = final_df['Cohort 2015'].astype('Int64')
final_df['Cohort 2016'] = final_df['Cohort 2016'].astype('Int64')

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv")