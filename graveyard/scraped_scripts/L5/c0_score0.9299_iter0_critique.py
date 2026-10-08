import pandas as pd

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_0/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_0/training_1.csv", index_col=0)

# Join on school_name
merged = pd.merge(df0, df1, left_on="school_name", right_on="school_name", how="inner")

# Create passing indicators
merged["passing_math"] = (merged["math_score"] >= 70).astype(int)
merged["passing_reading"] = (merged["reading_score"] >= 70).astype(int)

# Group by school_name and aggregate
agg = merged.groupby("school_name").agg(
    Total_Students=("student_name", "count"),
    student_name=("student_name", "count"),
    gender=("gender", "count"),
    grade=("grade", "count"),
    Average_Reading_Score=("reading_score", "mean"),
    Average_Math_Score=("math_score", "mean"),
    School_ID=("School ID", "first"),
    size=("size", "first"),
    Total_Budget=("budget", "first"),
    School_Type=("type", "first"),
    Total_Passing_Math=("passing_math", "sum"),
    Total_Passing_Reading=("passing_reading", "sum"),
).reset_index()

# Map School_Type to integer: both "district" and "charter" map to 1 as per target examples
def map_school_type(t):
    if isinstance(t, str):
        t = t.strip().lower()
        if t in ("district", "charter"):
            return 1
    return 1

agg["School Type"] = agg["School_Type"].map(map_school_type).astype(int)

# Rename columns to match target schema exactly
agg.rename(
    columns={
        "school_name": "School Name",
        "School_ID": "School ID",
        "Total_Budget": "Total Budget",
        "Total_Passing_Math": "Total Passing Math",
        "Total_Passing_Reading": "Total Passing Reading",
        "Average_Reading_Score": "Average Reading Score",
        "Average_Math_Score": "Average Math Score",
    },
    inplace=True,
)

# Round average scores to int
agg["Average Reading Score"] = agg["Average Reading Score"].round().astype(int)
agg["Average Math Score"] = agg["Average Math Score"].round().astype(int)

# Cast integer columns
agg["Total Students"] = agg["Total_Students"].astype(int)
agg["student_name"] = agg["student_name"].astype(int)
agg["gender"] = agg["gender"].astype(int)
agg["grade"] = agg["grade"].astype(int)
agg["School ID"] = agg["School ID"].astype(int)
agg["size"] = agg["size"].astype(int)
agg["Total Budget"] = agg["Total Budget"].astype(int)
agg["Total Passing Math"] = agg["Total Passing Math"].astype(int)
agg["Total Passing Reading"] = agg["Total Passing Reading"].astype(int)

# Select columns in target schema order
result = agg[
    [
        "School Name",
        "School Type",
        "Total Students",
        "student_name",
        "gender",
        "grade",
        "Average Reading Score",
        "Average Math Score",
        "School ID",
        "size",
        "Total Budget",
        "Total Passing Math",
        "Total Passing Reading",
    ]
]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_0/target_multisource_mcts.csv", index=False)