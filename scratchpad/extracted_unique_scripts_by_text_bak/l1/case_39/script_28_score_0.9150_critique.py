import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

# Join on 'State'
df = pd.merge(df0, df1, on="State", how="inner", suffixes=("_x", "_y"))

# Group by leftmost string columns that are unique identifiers in target
group_by_cols = ["State", "Participation_x", "Participation_y"]

# Aggregations:
# Float columns: mean
# Integer columns: sum
agg_dict = {
    "English": "mean",
    "Math_x": "mean",
    "Reading": "mean",
    "Science": "mean",
    "Composite": "mean",
    "Evidence-Based Reading and Writing": "sum",
    "Math_y": "sum",
    "Total": "sum"
}

df = df.groupby(group_by_cols, as_index=False).agg(agg_dict)

# Ensure integer columns have integer dtype
df["Evidence-Based Reading and Writing"] = df["Evidence-Based Reading and Writing"].astype("Int64")
df["Math_y"] = df["Math_y"].astype("Int64")
df["Total"] = df["Total"].astype("Int64")

# Reorder columns to match target schema exactly
df = df[[
    "State",
    "Participation_x",
    "English",
    "Math_x",
    "Reading",
    "Science",
    "Composite",
    "Participation_y",
    "Evidence-Based Reading and Writing",
    "Math_y",
    "Total"
]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)