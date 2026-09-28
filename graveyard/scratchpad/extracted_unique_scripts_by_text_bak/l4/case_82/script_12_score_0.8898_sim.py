import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

df = pd.merge(s4, s2, on="Institution", how="inner")
df = pd.merge(df, s1, on="Institution", how="inner")
df = pd.merge(df, s3, on="Institution", how="inner")
df = pd.merge(df, s0, on="Institution", how="inner")

df = df.rename(columns={
    "year 2014": "persist 2014",
    "year 2015": "persist 2015",
    "year 2016": "persist 2016"
})

cols = ['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
        'persist 2014', 'persist 2015', 'persist 2016',
        'Cohort 2014', 'Cohort 2015', 'Cohort 2016']

df = df[cols]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv")