import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

df12 = pd.merge(df1, df2, left_on="name", right_on="school", how="inner").drop(columns=["school"])

df_all = pd.merge(df12, df0, left_on="name", right_on="school", how="inner")

agg = df_all.groupby(["School ID", "name", "type", "size", "budget"]).agg(
    **{
        "Average Math Score": ("math_score", "mean"),
        "Average Reading Score": ("reading_score", "mean"),
        "Number Passing Math": (lambda x: (x >= 65).sum(), "math_score"),
        "Number Passing Reading": (lambda x: (x >= 65).sum(), "reading_score"),
    }
)

# The above agg syntax is invalid, fix with named aggregations properly:
agg = df_all.groupby(["School ID", "name", "type", "size", "budget"]).agg(
    Average_Math_Score = ("math_score", "mean"),
    Average_Reading_Score = ("reading_score", "mean"),
    Number_Passing_Math = (lambda x: (x >= 65).sum(), "math_score"),
    Number_Passing_Reading = (lambda x: (x >= 65).sum(), "reading_score"),
)

# The lambda aggregation syntax is incorrect, correct approach:
agg = df_all.groupby(["School ID", "name", "type", "size", "budget"]).agg(
    Average_Math_Score = ("math_score", "mean"),
    Average_Reading_Score = ("reading_score", "mean"),
    Number_Passing_Math = ("math_score", lambda x: (x >= 65).sum()),
    Number_Passing_Reading = ("reading_score", lambda x: (x >= 65).sum()),
)

agg = agg.reset_index()

agg = agg.rename(columns={
    "Average_Math_Score": "Average Math Score",
    "Average_Reading_Score": "Average Reading Score",
    "Number_Passing_Math": "Number Passing Math",
    "Number_Passing_Reading": "Number Passing Reading"
})

agg["Average Math Score"] = agg["Average Math Score"].astype(float)
agg["Average Reading Score"] = agg["Average Reading Score"].astype(float)
agg["Number Passing Math"] = agg["Number Passing Math"].astype(int)
agg["Number Passing Reading"] = agg["Number Passing Reading"].astype(int)
agg["School ID"] = agg["School ID"].astype(int)
agg["size"] = agg["size"].astype(int)
agg["budget"] = agg["budget"].astype(int)

agg = agg[["School ID", "name", "type", "size", "budget", "Average Math Score", "Average Reading Score", "Number Passing Math", "Number Passing Reading"]]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)