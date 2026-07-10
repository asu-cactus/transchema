import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

union_014 = pd.concat([s0.rename(columns={'year 2016':'persist 2016'}),
                       s1.rename(columns={'year 2014':'persist 2014'}),
                       s3.rename(columns={'year 2015':'persist 2015'})],
                      ignore_index=True)

union_014 = union_014.groupby('Institution', as_index=False).agg({
    'persist 2014': 'first',
    'persist 2015': 'first',
    'persist 2016': 'first'
})

join_1 = pd.merge(union_014, s2, on='Institution', how='outer')

join_2 = pd.merge(join_1, s4, on='Institution', how='outer')

cols = ['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
        'persist 2014', 'persist 2015', 'persist 2016',
        'Cohort 2014', 'Cohort 2015', 'Cohort 2016']

result = join_2[cols]

result['persist 2014'] = pd.to_numeric(result['persist 2014'], errors='coerce').astype('Int64')
result['persist 2015'] = pd.to_numeric(result['persist 2015'], errors='coerce').astype('Int64')
result['persist 2016'] = pd.to_numeric(result['persist 2016'], errors='coerce').astype('Int64')
result['Cohort 2014'] = pd.to_numeric(result['Cohort 2014'], errors='coerce').astype('Int64')
result['Cohort 2015'] = pd.to_numeric(result['Cohort 2015'], errors='coerce').astype('Int64')
result['Cohort 2016'] = pd.to_numeric(result['Cohort 2016'], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)