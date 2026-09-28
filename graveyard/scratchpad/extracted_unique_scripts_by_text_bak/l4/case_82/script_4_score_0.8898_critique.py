import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

# Join Source4_82_4 and Source4_82_2 on Institution
join_1 = pd.merge(df4, df2, on="Institution", how="inner")

# Join with Source4_82_1 (year 2014)
join_2 = pd.merge(join_1, df1, on="Institution", how="inner")

# Join with Source4_82_3 (year 2015)
join_3 = pd.merge(join_2, df3, on="Institution", how="inner")

# Join with Source4_82_0 (year 2016)
final_join = pd.merge(join_3, df0, on="Institution", how="inner")

# Select and rename columns to match target schema
final_df = final_join[[
    "Institution",
    "(Fall 2011)",
    "(Fall 2012)",
    "(Fall 2013)",
    "(Fall 2014)",
    "year 2014",
    "year 2015",
    "year 2016",
    "Cohort 2014",
    "Cohort 2015",
    "Cohort 2016"
]].copy()

final_df.rename(columns={
    "year 2014": "persist 2014",
    "year 2015": "persist 2015",
    "year 2016": "persist 2016"
}, inplace=True)

# Convert persist and cohort columns to integer type (target schema expects integer)
for col in ["persist 2014", "persist 2015", "persist 2016", "Cohort 2014", "Cohort 2015", "Cohort 2016"]:
    final_df[col] = final_df[col].astype(int)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)