import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
union_013 = pd.concat([s0, s1, s3], ignore_index=True)

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
joined_1 = pd.merge(union_013, s2, on="Institution", how="outer")

s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)
final = pd.merge(joined_1, s4, on="Institution", how="outer")

final = final.rename(columns={
    "year 2014": "persist 2014",
    "year 2015": "persist 2015",
    "year 2016": "persist 2016"
})

cols = ['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
        'persist 2014', 'persist 2015', 'persist 2016',
        'Cohort 2014', 'Cohort 2015', 'Cohort 2016']

final = final[cols]

for c in ['(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)']:
    final[c] = pd.to_numeric(final[c], errors='coerce')

for c in ['persist 2014', 'persist 2015', 'persist 2016', 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']:
    final[c] = pd.to_numeric(final[c], errors='coerce').astype('Int64')

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)