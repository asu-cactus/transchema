import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)  # student-level
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)  # school info
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)  # school aggregates

# Join Source1 and Source2 on school name
df12 = pd.merge(df1, df2, left_on="name", right_on="school", how="inner").drop(columns=["school"])

# Join the above with Source0 on school name
df_all = pd.merge(df12, df0, left_on="name", right_on="school", how="inner")

# Group by School ID only, aggregate by taking first for non-aggregated columns and aggregated columns
agg = df_all.groupby("School ID").agg(
    name=("name", "first"),
    type=("type", "first"),
    size=("size", "first"),
    budget=("budget", "first"),
    **{
        "Average Math Score": ("Average Math Score", "first"),
        "Average Reading Score": ("Average Reading Score", "first"),
        "Number Passing Math": ("Number Passing Math", "first"),
        "Number Passing Reading": ("Number Passing Reading", "first"),
    }
).reset_index()

# Ensure correct dtypes
agg["School ID"] = agg["School ID"].astype(int)
agg["name"] = agg["name"].astype(str)
agg["type"] = agg["type"].astype(str)
agg["size"] = agg["size"].astype(int)
agg["budget"] = agg["budget"].astype(int)
agg["Average Math Score"] = agg["Average Math Score"].astype(float)
agg["Average Reading Score"] = agg["Average Reading Score"].astype(float)
agg["Number Passing Math"] = agg["Number Passing Math"].astype(int)
agg["Number Passing Reading"] = agg["Number Passing Reading"].astype(int)

# Reorder columns to match target schema exactly
agg = agg[["School ID", "name", "type", "size", "budget", "Average Math Score", "Average Reading Score", "Number Passing Math", "Number Passing Reading"]]

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)