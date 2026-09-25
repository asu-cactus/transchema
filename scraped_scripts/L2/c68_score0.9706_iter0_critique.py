import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_68/training_1.csv", index_col=0)

# Aggregate student data by school_name
agg_students = df1.groupby("school_name").agg(
    Total_Students=("student_name", "count"),
    Average_Math_Score=("math_score", "mean"),
    Average_Reading_Score=("reading_score", "mean")
).reset_index()

# Join school data with aggregated student data on school_name
merged = pd.merge(df0, agg_students, on="school_name", how="inner")

# Group by school_name and type to aggregate budget (sum) and ensure uniqueness
result = merged.groupby(["school_name", "type"], as_index=False).agg(
    Total_Students=("Total_Students", "sum"),
    Total_School_Budget=("budget", "sum"),
    Average_Math_Score=("Average_Math_Score", "mean"),
    Average_Reading_Score=("Average_Reading_Score", "mean")
)

# Rename columns to match target schema exactly
result = result.rename(columns={
    "Total_Students": "Total Students",
    "Total_School_Budget": "Total School Budget",
    "Average_Math_Score": "Average Math Score",
    "Average_Reading_Score": "Average Reading Score"
})

# Ensure correct data types
result["Total Students"] = result["Total Students"].astype(int)
result["Total School Budget"] = result["Total School Budget"].astype(int)
result["Average Math Score"] = result["Average Math Score"].astype(float)
result["Average Reading Score"] = result["Average Reading Score"].astype(float)

# Reorder columns as per target schema
result = result[["school_name", "type", "Total Students", "Total School Budget", "Average Math Score", "Average Reading Score"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_68/target_multisource_mcts.csv", index=False)