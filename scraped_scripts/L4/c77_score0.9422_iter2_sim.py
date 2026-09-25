import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

df2_renamed = df2.rename(columns={"school": "name"})

df1_2 = pd.merge(df1, df2_renamed, on="name", how="inner")

df0_unpivot = pd.melt(df0, id_vars=["Student ID", "name", "gender", "grade", "school"], value_vars=["reading_score", "math_score"], var_name="type", value_name="size")
df0_unpivot["type"] = df0_unpivot["type"].str.replace("_score", "").str.capitalize()

agg_df0 = df0_unpivot.groupby("school").agg(
    Average_Math_Score = ("size", lambda x: x[df0_unpivot.loc[x.index, "type"] == "Math"].mean()),
    Average_Reading_Score = ("size", lambda x: x[df0_unpivot.loc[x.index, "type"] == "Reading"].mean()),
    Number_Passing_Math = ("size", lambda x: (x[df0_unpivot.loc[x.index, "type"] == "Math"] >= 60).sum()),
    Number_Passing_Reading = ("size", lambda x: (x[df0_unpivot.loc[x.index, "type"] == "Reading"] >= 60).sum())
).reset_index().rename(columns={"school": "name"})

df_final = pd.merge(df1_2, agg_df0, on="name", how="inner")

df_final = df_final.rename(columns={
    "School ID": "School ID",
    "name": "name",
    "type": "type",
    "size": "size",
    "budget": "budget",
    "Average_Math_Score": "Average Math Score",
    "Average_Reading_Score": "Average Reading Score",
    "Number_Passing_Math": "Number Passing Math",
    "Number_Passing_Reading": "Number Passing Reading"
})

df_final = df_final[[
    "School ID", "name", "type", "size", "budget",
    "Average Math Score", "Average Reading Score",
    "Number Passing Math", "Number Passing Reading"
]]

df_final["School ID"] = df_final["School ID"].astype(int)
df_final["name"] = df_final["name"].astype(str)
df_final["type"] = df_final["type"].astype(str)
df_final["size"] = df_final["size"].astype(int)
df_final["budget"] = df_final["budget"].astype(int)
df_final["Average Math Score"] = df_final["Average Math Score"].astype(float)
df_final["Average Reading Score"] = df_final["Average Reading Score"].astype(float)
df_final["Number Passing Math"] = df_final["Number Passing Math"].astype(int)
df_final["Number Passing Reading"] = df_final["Number Passing Reading"].astype(int)

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)