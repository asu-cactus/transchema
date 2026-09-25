import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_1.csv", index_col=0)

agg_source0 = source0.groupby("size").agg(
    Total_Students=pd.NamedAgg(column="size", aggfunc="sum"),
    Total_School_Budget=pd.NamedAgg(column="budget", aggfunc="sum"),
).reset_index()

agg_source1 = source1.groupby("school_name").agg(
    Average_Math_Score=pd.NamedAgg(column="math_score", aggfunc="mean"),
    Average_Reading_Score=pd.NamedAgg(column="reading_score", aggfunc="mean"),
).reset_index()

# Join source0 and agg_source1 on school_name to get size and budget with average scores
merged = pd.merge(source0, agg_source1, on="school_name", how="inner")

# Now group by size to aggregate total students, total budget, and average scores
final = merged.groupby("size").agg(
    Total_Students=pd.NamedAgg(column="size", aggfunc="sum"),
    Total_School_Budget=pd.NamedAgg(column="budget", aggfunc="sum"),
    Average_Math_Score=pd.NamedAgg(column="Average_Math_Score", aggfunc="mean"),
    Average_Reading_Score=pd.NamedAgg(column="Average_Reading_Score", aggfunc="mean"),
).reset_index()

final = final.rename(columns={"size": "School Size"})

final["Total Students"] = final["Total_Students"].astype(int)
final["Total School Budget"] = final["Total_School_Budget"].astype(int)
final["Average Math Score"] = final["Average_Math_Score"].astype(float)
final["Average Reading Score"] = final["Average_Reading_Score"].astype(float)

final = final[["School Size", "Total Students", "Total School Budget", "Average Math Score", "Average Reading Score"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_42/target_multisource_mcts.csv", index=False)