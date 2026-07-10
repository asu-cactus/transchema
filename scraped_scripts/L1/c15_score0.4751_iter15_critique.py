import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

df0 = df0.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})
df1 = df1.rename(columns={"Participation": "Participation_y", "Math": "Math_y"})

df_merged = pd.merge(df0, df1, on="State", how="outer")

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

df_grouped = df_merged.groupby(
    ["State", "Participation_x", "Participation_y"], dropna=False, as_index=False
).agg(agg_dict)

# Ensure integer columns are integer dtype
df_grouped["Evidence-Based Reading and Writing"] = df_grouped["Evidence-Based Reading and Writing"].astype("Int64")
df_grouped["Math_y"] = df_grouped["Math_y"].astype("Int64")
df_grouped["Total"] = df_grouped["Total"].astype("Int64")

# Reorder columns to match target schema exactly
df_result = df_grouped[
    [
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
        "Total",
    ]
]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)