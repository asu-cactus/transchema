import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_30/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_30/training_1.csv", index_col=0)

agg = source1.groupby("school_name").agg(
    Student_ID=("Student ID", "nunique"),
    math_score=("math_score", "min"),
    reading_score=("reading_score", "max")
).reset_index()

merged = pd.merge(source0, agg, on="school_name", how="inner")

result = merged.rename(columns={
    "Student_ID": "Student ID",
    "budget": "budget",
    "math_score": "math_score",
    "reading_score": "reading_score"
})[["school_name", "Student ID", "budget", "math_score", "reading_score"]]

result["Student ID"] = result["Student ID"].astype(int)
result["budget"] = result["budget"].astype(int)
result["math_score"] = result["math_score"].astype(float)
result["reading_score"] = result["reading_score"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_30/target_multisource_mcts.csv", index=False)