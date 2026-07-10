import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

agg_df = df2.groupby("school").agg(
    Average_Math_Score=("math_score", "mean"),
    Average_Reading_Score=("reading_score", "mean"),
    Number_Passing_Math=("math_score", lambda x: (x >= 70).sum()),
    Number_Passing_Reading=("reading_score", lambda x: (x >= 70).sum()),
    School_Size=("school", "count")
).reset_index()

merged1 = pd.merge(agg_df, df1, left_on="school", right_on="name", how="inner")

final_df = pd.merge(merged1, df0, left_on="name", right_on="school", how="inner")

final_df = final_df.rename(columns={
    "school_x": "school",
    "Average_Math_Score": "Average Math Score",
    "Average_Reading_Score": "Average Reading Score",
    "Number_Passing_Math": "Number Passing Math",
    "Number_Passing_Reading": "Number Passing Reading",
    "School_Size": "School Size"
})

final_df = final_df[[
    "School ID", "name", "type", "size", "budget",
    "Average Math Score", "Average Reading Score",
    "Number Passing Math", "Number Passing Reading", "School Size"
]]

final_df["size"] = final_df["size"].astype(int)
final_df["budget"] = final_df["budget"].astype(int)
final_df["School ID"] = final_df["School ID"].astype(int)
final_df["Number Passing Math"] = final_df["Number Passing Math"].astype(int)
final_df["Number Passing Reading"] = final_df["Number Passing Reading"].astype(int)
final_df["School Size"] = final_df["School Size"].astype(int)
final_df["Average Math Score"] = final_df["Average Math Score"].astype(float)
final_df["Average Reading Score"] = final_df["Average Reading Score"].astype(float)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)