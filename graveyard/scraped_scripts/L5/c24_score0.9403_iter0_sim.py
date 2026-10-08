import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_24/training_1.csv", index_col=0)

agg = df0.groupby("school_name").agg({
    "Student ID": "mean",
    "math_score": "mean",
    "reading_score": "mean"
}).reset_index()

merged = pd.merge(agg, df1[["school_name", "budget"]], on="school_name", how="inner")

merged = merged.rename(columns={
    "Student ID": "Student ID",
    "budget": "budget",
    "math_score": "math_score",
    "reading_score": "reading_score",
    "school_name": "school_name"
})

merged["Student ID"] = merged["Student ID"].astype(int)
merged["budget"] = merged["budget"].astype(int)
merged["math_score"] = merged["math_score"].astype(float)
merged["reading_score"] = merged["reading_score"].astype(float)
merged["school_name"] = merged["school_name"].astype(str)

merged = merged[["school_name", "Student ID", "budget", "math_score", "reading_score"]]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length5_24/target_multisource_mcts.csv", index=False)