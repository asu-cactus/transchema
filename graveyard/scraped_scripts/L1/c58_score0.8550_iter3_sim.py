import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_58/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_58/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=["State", "Participation"], 
                       value_vars=["Evidence-Based Reading and Writing", "Math", "Total"],
                       var_name="variable", value_name="value")

df0_unpivot = df0_unpivot.rename(columns={"Participation": "Participation_x"})

df0_pivot = df0_unpivot.pivot_table(index=["State", "Participation_x"], 
                                   columns="variable", values="value").reset_index()

df1_renamed = df1.rename(columns={"Participation": "Participation_y", "Math": "Math_y"})

df_merged = pd.merge(df0_pivot, df1_renamed, on="State", how="inner")

df_merged = df_merged.rename(columns={
    "Evidence-Based Reading and Writing": "Evidence-Based Reading and Writing",
    "Math": "Math_x",
    "Total": "Total"
})

df_merged = df_merged[[
    "State", "Participation_x", "Evidence-Based Reading and Writing", "Math_x", "Total",
    "Participation_y", "English", "Math_y", "Reading", "Science", "Composite"
]]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_58/target_multisource_mcts.csv", index=False)