import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_1.csv", index_col=0)

df0_long = df0.melt(id_vars=["State", "Participation"], 
                    value_vars=["English", "Math", "Reading", "Science", "Composite"], 
                    var_name="Subject", value_name="Score")
df0_long = df0_long.rename(columns={"Participation": "Participation_x"})

df0_pivot = df0_long.pivot_table(index=["State", "Participation_x"], 
                                columns="Subject", values="Score").reset_index()

df_merged = pd.merge(df0_pivot, df1, how="inner", on="State")

df_merged = df_merged.rename(columns={
    "Participation": "Participation_y",
    "Math_x": "Math_x",
    "Math_y": "Math",
    "Math": "Math_y"
})

df_merged["Math_x"] = df_merged["Math_x"].astype(float)
df_merged["English"] = df_merged["English"].astype(float)
df_merged["Reading"] = df_merged["Reading"].astype(float)
df_merged["Science"] = df_merged["Science"].astype(float)
df_merged["Composite"] = df_merged["Composite"].astype(float)
df_merged["Evidence-Based Reading and Writing"] = df_merged["Evidence-Based Reading and Writing"].astype("Int64")
df_merged["Math_y"] = df_merged["Math"].astype("Int64")
df_merged["Total"] = df_merged["Total"].astype("Int64")

df_merged = df_merged[[
    "State", "Participation_x", "English", "Math_x", "Reading", "Science", "Composite",
    "Participation_y", "Evidence-Based Reading and Writing", "Math_y", "Total"
]]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_33/target_multisource_mcts.csv", index=False)