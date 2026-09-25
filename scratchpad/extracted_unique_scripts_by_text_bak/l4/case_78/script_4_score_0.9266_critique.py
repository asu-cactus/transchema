import pandas as pd

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

# Aggregate Source4_78_2 to get School Size (count of students per school)
df2_agg = df2.groupby("school", as_index=False).agg(School_Size=("Student ID", "count"))

# Join Source4_78_1 and Source4_78_0 on name=school
join_1_0 = pd.merge(df1, df0, left_on="name", right_on="school", how="inner")

# Join the above with aggregated df2 on name=school
joined = pd.merge(join_1_0, df2_agg, left_on="name", right_on="school", how="inner")

# Group by leftmost columns of target schema
grouped = joined.groupby(
    ["School ID", "name", "type", "size", "budget"], as_index=False
).agg({
    "Average Math Score": "mean",
    "Average Reading Score": "mean",
    "Number Passing Math": "sum",
    "Number Passing Reading": "sum",
    "School_Size": "max"
})

# Rename columns to match target schema
grouped = grouped.rename(columns={"School_Size": "School Size"})

# Cast columns to correct types
grouped = grouped.astype({
    "School ID": "int64",
    "name": "string",
    "type": "string",
    "size": "int64",
    "budget": "int64",
    "Average Math Score": "float64",
    "Average Reading Score": "float64",
    "Number Passing Math": "int64",
    "Number Passing Reading": "int64",
    "School Size": "int64"
})

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)