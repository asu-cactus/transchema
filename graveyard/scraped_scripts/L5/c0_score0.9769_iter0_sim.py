import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_0/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_0/training_1.csv", index_col=0)

agg = df1.groupby("school_name").agg(
    Total_Students=("student_name", "count"),
    student_name=("student_name", "count"),
    gender=("gender", "count"),
    grade=("grade", "count"),
    Average_Reading_Score=("reading_score", "mean"),
    Average_Math_Score=("math_score", "mean"),
).reset_index()

merged = pd.merge(df0, agg, left_on="school_name", right_on="school_name", how="inner")

def map_school_type(t):
    if isinstance(t, str):
        t = t.strip().lower()
        if t == "district":
            return 1
        elif t == "charter":
            return 1
    return 1

merged["School Type"] = merged["type"].map(map_school_type).fillna(1).astype(int)
merged["School Name"] = merged["school_name"]
merged["Total Students"] = merged["Total_Students"].astype(int)
merged["student_name"] = merged["student_name"].astype(int)
merged["gender"] = merged["gender"].astype(int)
merged["grade"] = merged["grade"].astype(int)
merged["Average Reading Score"] = merged["Average_Reading_Score"].round().astype(int)
merged["Average Math Score"] = merged["Average_Math_Score"].round().astype(int)
merged["School ID"] = merged["School ID"].astype(int)
merged["size"] = merged["size"].astype(int)
merged["Total Budget"] = merged["budget"].astype(int)
merged["Total Passing Math"] = 0
merged["Total Passing Reading"] = 0

result = merged[
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

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_0/target_multisource_mcts.csv", index=False)