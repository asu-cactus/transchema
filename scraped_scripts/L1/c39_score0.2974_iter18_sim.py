import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=["State", "Participation"], 
                       value_vars=["English", "Math", "Reading", "Science", "Composite"],
                       var_name="Participation_x", value_name="Value")

df0_pivot = df0_unpivot.pivot_table(index=["State", "Participation", "Participation_x"], 
                                   columns="Participation_x", values="Value", aggfunc='first').reset_index()

df0_pivot = df0_pivot.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})

df_merged = pd.merge(df0_pivot, df1, how="inner", on="State", suffixes=("", "_y"))

df_merged = df_merged.rename(columns={"Participation": "Participation_y", "Math": "Math_y"})

df_merged = df_merged[[
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

df_merged["Evidence-Based Reading and Writing"] = df_merged["Evidence-Based Reading and Writing"].astype("Int64")
df_merged["Math_y"] = df_merged["Math_y"].astype("Int64")
df_merged["Total"] = df_merged["Total"].astype("Int64")

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)