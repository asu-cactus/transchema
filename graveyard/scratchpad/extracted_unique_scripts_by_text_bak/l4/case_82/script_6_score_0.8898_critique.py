import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

# Rename year columns in df0, df1, df3 to persist columns to match target schema
df0 = df0.rename(columns={"year 2016": "persist 2016"})
df1 = df1.rename(columns={"year 2014": "persist 2014"})
df3 = df3.rename(columns={"year 2015": "persist 2015"})

# Join all tables on Institution
join_0 = pd.merge(df2, df1, on="Institution", how="inner")
join_1 = pd.merge(join_0, df3, on="Institution", how="inner")
join_2 = pd.merge(join_1, df0, on="Institution", how="inner")
final_df = pd.merge(join_2, df4, on="Institution", how="inner")

# Group by Institution and aggregate
# For Fall columns and Cohort columns, use mean (float columns)
# For persist columns, use sum (integer counts)
agg_dict = {
    "(Fall 2011)": "mean",
    "(Fall 2012)": "mean",
    "(Fall 2013)": "mean",
    "(Fall 2014)": "mean",
    "persist 2014": "sum",
    "persist 2015": "sum",
    "persist 2016": "sum",
    "Cohort 2014": "mean",
    "Cohort 2015": "mean",
    "Cohort 2016": "mean"
}

final_df = final_df.groupby("Institution", as_index=False).agg(agg_dict)

# Cast persist and Cohort columns to integer as in target schema
for col in ["persist 2014", "persist 2015", "persist 2016", "Cohort 2014", "Cohort 2015", "Cohort 2016"]:
    final_df[col] = final_df[col].round().astype(int)

# Reorder columns to match target schema exactly
final_df = final_df[[
    "Institution",
    "(Fall 2011)", "(Fall 2012)", "(Fall 2013)", "(Fall 2014)",
    "persist 2014", "persist 2015", "persist 2016",
    "Cohort 2014", "Cohort 2015", "Cohort 2016"
]]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)