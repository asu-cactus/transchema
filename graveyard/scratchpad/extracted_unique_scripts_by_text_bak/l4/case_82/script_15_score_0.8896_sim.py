import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

join_1_2 = pd.merge(s2, s1, on="Institution", how="inner")
join_0 = pd.merge(join_1_2, s0, on="Institution", how="inner")
join_3 = pd.merge(join_0, s3, on="Institution", how="inner")
final_join = pd.merge(join_3, s4, on="Institution", how="inner")

final = final_join[[
    "Institution",
    "(Fall 2011)", "(Fall 2012)", "(Fall 2013)", "(Fall 2014)",
    "year 2014", "year 2015", "year 2016",
    "Cohort 2014", "Cohort 2015", "Cohort 2016"
]].copy()

final.rename(columns={
    "year 2014": "persist 2014",
    "year 2015": "persist 2015",
    "year 2016": "persist 2016"
}, inplace=True)

final["persist 2014"] = final["persist 2014"].astype("Int64")
final["persist 2015"] = final["persist 2015"].astype("Int64")
final["persist 2016"] = final["persist 2016"].astype("Int64")
final["Cohort 2014"] = final["Cohort 2014"].astype("Int64")
final["Cohort 2015"] = final["Cohort 2015"].astype("Int64")
final["Cohort 2016"] = final["Cohort 2016"].astype("Int64")

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)