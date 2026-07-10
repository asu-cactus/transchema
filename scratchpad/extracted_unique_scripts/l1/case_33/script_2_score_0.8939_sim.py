import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={
    "Participation": "Participation_x",
    "Math": "Math_x"
})

df1_renamed = df1.rename(columns={
    "Participation": "Participation_y",
    "Math": "Math_y"
})

merged = pd.merge(df0_renamed, df1_renamed, on="State", how="inner")

grouped = merged.groupby(["Participation_x", "Participation_y"], as_index=False).agg({
    "State": "first",
    "English": "mean",
    "Math_x": "mean",
    "Reading": "mean",
    "Science": "mean",
    "Composite": "mean",
    "Evidence-Based Reading and Writing": "mean",
    "Math_y": "mean",
    "Total": "mean"
})

grouped["Evidence-Based Reading and Writing"] = grouped["Evidence-Based Reading and Writing"].round().astype("Int64")
grouped["Math_y"] = grouped["Math_y"].round().astype("Int64")
grouped["Total"] = grouped["Total"].round().astype("Int64")

cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
        'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

result = grouped[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_33/target_multisource_mcts.csv", index=False)