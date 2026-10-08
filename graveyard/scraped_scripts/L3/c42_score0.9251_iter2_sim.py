import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="school_name")

agg = merged.groupby("size").agg(
    Total_Students=("size", "sum"),
    Total_School_Budget=("budget", "sum"),
    Average_Math_Score=("math_score", "mean"),
    Average_Reading_Score=("reading_score", "mean"),
).reset_index()

agg = agg.rename(columns={"size": "School Size"})

agg["School Size"] = agg["School Size"].astype(int)
agg["Total_Students"] = agg["Total_Students"].astype(int)
agg["Total_School_Budget"] = agg["Total_School_Budget"].astype(int)
agg["Average_Math_Score"] = agg["Average_Math_Score"].astype(float)
agg["Average_Reading_Score"] = agg["Average_Reading_Score"].astype(float)

agg.columns = [
    "School Size",
    "Total Students",
    "Total School Budget",
    "Average Math Score",
    "Average Reading Score",
]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_42/target_multisource_mcts.csv", index=False)