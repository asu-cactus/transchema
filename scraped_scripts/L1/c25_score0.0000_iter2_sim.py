import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_25/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_25/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_25/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df0_unpivot = pd.melt(df0, id_vars=["State", "Participation"], 
                      value_vars=["English", "Math", "Reading", "Science", "Composite"],
                      var_name="Participation_x", value_name="Value")

df0_pivot = df0_unpivot.pivot_table(index=["State", "Participation", "Participation_x"], 
                                    columns="Participation_x", values="Value").reset_index()

df0_pivot.rename(columns={"Participation": "Participation_y", "Math": "Math_x"}, inplace=True)

df_merged = pd.merge(df0_pivot, df1, how="inner", left_on=["State", "Participation_y"], right_on=["State", "Participation"])

df_merged.rename(columns={"Math": "Math_y"}, inplace=True)

result = df_merged[[
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

result["Evidence-Based Reading and Writing"] = result["Evidence-Based Reading and Writing"].astype("Int64")
result["Math_y"] = result["Math_y"].astype("Int64")
result["Total"] = result["Total"].astype("Int64")

result.to_csv(target_path, index=False)