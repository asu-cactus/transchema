import pandas as pd

# Read all source files with index_col=0 to ignore the first numerical index column
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

# Rename year columns in s0, s1, s3 to match target persist columns before merging
s0 = s0.rename(columns={"year 2016": "persist 2016"})
s1 = s1.rename(columns={"year 2014": "persist 2014"})
s3 = s3.rename(columns={"year 2015": "persist 2015"})

# Merge s2 and s4 on Institution
df = pd.merge(s2, s4, on="Institution", how="inner")

# Merge with s0, s1, s3 on Institution
df = pd.merge(df, s0, on="Institution", how="inner")
df = pd.merge(df, s1, on="Institution", how="inner")
df = pd.merge(df, s3, on="Institution", how="inner")

# Group by Institution to ensure unique rows (no aggregation needed)
df = df.groupby("Institution", as_index=False).first()

# Select and reorder columns to match target schema
target_columns = [
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
]

result = df[target_columns]

# Convert persist and Cohort columns to integer type (target schema)
for col in ["persist 2014", "persist 2015", "persist 2016", "Cohort 2014", "Cohort 2015", "Cohort 2016"]:
    result[col] = result[col].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)