import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

# Join all source tables on 'Institution'
df = pd.merge(s2, s1, on="Institution", how="inner")
df = pd.merge(df, s3, on="Institution", how="inner")
df = pd.merge(df, s0, on="Institution", how="inner")
df = pd.merge(df, s4, on="Institution", how="inner")

# Rename year columns to persist columns as per target schema
df = df.rename(columns={
    "year 2014": "persist 2014",
    "year 2015": "persist 2015",
    "year 2016": "persist 2016"
})

# Select and order columns exactly as target schema
df = df[[
    "Institution",
    "(Fall 2011)", "(Fall 2012)", "(Fall 2013)", "(Fall 2014)",
    "persist 2014", "persist 2015", "persist 2016",
    "Cohort 2014", "Cohort 2015", "Cohort 2016"
]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv")