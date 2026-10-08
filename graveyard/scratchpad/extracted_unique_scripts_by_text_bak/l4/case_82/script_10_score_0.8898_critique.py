import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

# Join sources on Institution using INNER JOIN to keep only institutions present in all sources
df = pd.merge(s0, s1, on="Institution", how="inner")
df = pd.merge(df, s3, on="Institution", how="inner")
df = pd.merge(df, s4, on="Institution", how="inner")
df = pd.merge(df, s2, on="Institution", how="inner")

# Create persist columns from year columns, fill missing with 0 and convert to int
persist_2014 = df["year 2014"].fillna(0).astype(int)
persist_2015 = df["year 2015"].fillna(0).astype(int)
persist_2016 = df["year 2016"].fillna(0).astype(int)

# Cohort columns from s4, fill missing with 0 and convert to int
cohort_2014 = df["Cohort 2014"].fillna(0).astype(int)
cohort_2015 = df["Cohort 2015"].fillna(0).astype(int)
cohort_2016 = df["Cohort 2016"].fillna(0).astype(int)

# Assemble final dataframe with correct columns and types
result = pd.DataFrame({
    "Institution": df["Institution"],
    "(Fall 2011)": df["(Fall 2011)"].astype(float),
    "(Fall 2012)": df["(Fall 2012)"].astype(float),
    "(Fall 2013)": df["(Fall 2013)"].astype(float),
    "(Fall 2014)": df["(Fall 2014)"].astype(float),
    "persist 2014": persist_2014,
    "persist 2015": persist_2015,
    "persist 2016": persist_2016,
    "Cohort 2014": cohort_2014,
    "Cohort 2015": cohort_2015,
    "Cohort 2016": cohort_2016
})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)