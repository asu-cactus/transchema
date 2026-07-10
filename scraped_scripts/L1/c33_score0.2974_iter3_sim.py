import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=["State", "Participation"], 
                       value_vars=["English", "Math", "Reading", "Science", "Composite"],
                       var_name="Participation_x", value_name="Score")

df0_pivot = df0_unpivot.pivot_table(index=["State", "Participation", "Participation_x"], 
                                   columns="Participation_x", values="Score").reset_index()

df0_pivot = df0_pivot.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})

df1_renamed = df1.rename(columns={"Participation": "Participation_y", "Math": "Math_y"})

merged = pd.merge(df0_pivot, df1_renamed, on="State", how="inner")

merged = merged[["State", "Participation_x", "English", "Math_x", "Reading", "Science", "Composite",
                 "Participation_y", "Evidence-Based Reading and Writing", "Math_y", "Total"]]

merged["Evidence-Based Reading and Writing"] = merged["Evidence-Based Reading and Writing"].astype("Int64")
merged["Math_y"] = merged["Math_y"].astype("Int64")
merged["Total"] = merged["Total"].astype("Int64")

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_33/target_multisource_mcts.csv", index=False)