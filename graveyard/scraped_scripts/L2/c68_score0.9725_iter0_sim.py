import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_68/training_1.csv", index_col=0)

agg = df1.groupby("school_name").agg(
    Average_Math_Score=("math_score", "mean"),
    Average_Reading_Score=("reading_score", "mean"),
    Total_Students=("student_name", "count")
).reset_index()

merged = pd.merge(df0, agg, on="school_name", how="inner")

result = merged.rename(columns={
    "size": "Total Students",
    "budget": "Total School Budget",
    "Average_Math_Score": "Average Math Score",
    "Average_Reading_Score": "Average Reading Score"
})

result = result[["school_name", "type", "Total Students", "Total School Budget", "Average Math Score", "Average Reading Score"]]

result["Total Students"] = result["Total Students"].astype(int)
result["Total School Budget"] = result["Total School Budget"].astype(int)
result["Average Math Score"] = result["Average Math Score"].astype(float)
result["Average Reading Score"] = result["Average Reading Score"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_68/target_multisource_mcts.csv", index=False)