import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

u = pd.concat([s0, s1, s3], ignore_index=True)

j1 = pd.merge(u, s2, on="Institution", how="outer")

j2 = pd.merge(j1, s4, on="Institution", how="outer")

j2.rename(columns={
    "year 2014": "persist 2014",
    "year 2015": "persist 2015",
    "year 2016": "persist 2016"
}, inplace=True)

target_cols = ['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
               'persist 2014', 'persist 2015', 'persist 2016',
               'Cohort 2014', 'Cohort 2015', 'Cohort 2016']

result = j2[target_cols]

result['persist 2014'] = pd.to_numeric(result['persist 2014'], errors='coerce').astype('Int64')
result['persist 2015'] = pd.to_numeric(result['persist 2015'], errors='coerce').astype('Int64')
result['persist 2016'] = pd.to_numeric(result['persist 2016'], errors='coerce').astype('Int64')
result['Cohort 2014'] = pd.to_numeric(result['Cohort 2014'], errors='coerce').astype('Int64')
result['Cohort 2015'] = pd.to_numeric(result['Cohort 2015'], errors='coerce').astype('Int64')
result['Cohort 2016'] = pd.to_numeric(result['Cohort 2016'], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)