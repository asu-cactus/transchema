import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

df01 = pd.merge(s0, s1, on="Institution", how="outer")
df013 = pd.merge(df01, s3, on="Institution", how="outer")
df0134 = pd.merge(df013, s4, on="Institution", how="outer")
df_all = pd.merge(df0134, s2, on="Institution", how="outer")

df_all["persist 2014"] = df_all["year 2014"].fillna(0).astype(int)
df_all["persist 2015"] = df_all["year 2015"].fillna(0).astype(int)
df_all["persist 2016"] = df_all["year 2016"].fillna(0).astype(int)

df_all["Cohort 2014"] = df_all["Cohort 2014"].fillna(0).astype(int)
df_all["Cohort 2015"] = df_all["Cohort 2015"].fillna(0).astype(int)
df_all["Cohort 2016"] = df_all["Cohort 2016"].fillna(0).astype(int)

df_all = df_all.groupby("Institution", as_index=False).agg({
    "Cohort 2014": "sum",
    "Cohort 2015": "sum",
    "Cohort 2016": "sum",
    "persist 2014": "sum",
    "persist 2015": "sum",
    "persist 2016": "sum",
    "(Fall 2011)": "mean",
    "(Fall 2012)": "mean",
    "(Fall 2013)": "mean",
    "(Fall 2014)": "mean"
})

df_all["(Fall 2011)"] = df_all["(Fall 2011)"].astype(float)
df_all["(Fall 2012)"] = df_all["(Fall 2012)"].astype(float)
df_all["(Fall 2013)"] = df_all["(Fall 2013)"].astype(float)
df_all["(Fall 2014)"] = df_all["(Fall 2014)"].astype(float)

df_all = df_all[[
    "Institution",
    "(Fall 2011)",
    "(Fall 2012)",
    "(Fall 2013)",
    "(Fall 2014)",
    "persist 2014",
    "persist 2015",
    "persist 2016",
    "Cohort 2014",
    "Cohort 2015",
    "Cohort 2016"
]]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)