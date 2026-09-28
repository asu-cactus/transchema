import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_45/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_45/training_1.csv", index_col=0)

df0 = df0.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})
df1 = df1.rename(columns={"Participation": "Participation_y", "Math": "Math_y"})

df_merged = pd.merge(df0, df1, on="State", how="inner")

df_result = df_merged[[
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

df_result["Evidence-Based Reading and Writing"] = df_result["Evidence-Based Reading and Writing"].astype("Int64")
df_result["Math_y"] = df_result["Math_y"].astype("Int64")
df_result["Total"] = df_result["Total"].astype("Int64")

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_45/target_multisource_mcts.csv", index=False)