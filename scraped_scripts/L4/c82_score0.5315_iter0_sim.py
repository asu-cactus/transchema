import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

grouped_source2 = source2.groupby('Institution', as_index=False).mean()

joined_1 = pd.merge(grouped_source2, source1, on='Institution', how='outer')
joined_2 = pd.merge(joined_1, source3, on='Institution', how='outer')
joined_3 = pd.merge(joined_2, source0, on='Institution', how='outer')
final = pd.merge(joined_3, source4, on='Institution', how='outer')

final = final.rename(columns={
    'year 2014': 'persist 2014',
    'year 2015': 'persist 2015',
    'year 2016': 'persist 2016'
})

final = final[['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
               'persist 2014', 'persist 2015', 'persist 2016',
               'Cohort 2014', 'Cohort 2015', 'Cohort 2016']]

final['persist 2014'] = final['persist 2014'].astype('Int64')
final['persist 2015'] = final['persist 2015'].astype('Int64')
final['persist 2016'] = final['persist 2016'].astype('Int64')
final['Cohort 2014'] = final['Cohort 2014'].astype('Int64')
final['Cohort 2015'] = final['Cohort 2015'].astype('Int64')
final['Cohort 2016'] = final['Cohort 2016'].astype('Int64')

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)