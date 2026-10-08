import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

join_0 = pd.merge(df2, df1, on="Institution", how="inner")
join_1 = pd.merge(join_0, df3, on="Institution", how="inner")
join_2 = pd.merge(join_1, df0, on="Institution", how="inner")
final_df = pd.merge(join_2, df4, on="Institution", how="inner")

final_df = final_df.rename(columns={
    "year 2014": "persist 2014",
    "year 2015": "persist 2015",
    "year 2016": "persist 2016"
})

final_df = final_df[[
    "Institution",
    "(Fall 2011)", "(Fall 2012)", "(Fall 2013)", "(Fall 2014)",
    "persist 2014", "persist 2015", "persist 2016",
    "Cohort 2014", "Cohort 2015", "Cohort 2016"
]]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv")