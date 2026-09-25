import pandas as pd

# Load sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

# Rename columns in source0 for join compatibility
source0 = source0.rename(columns={"school": "name"})

# Join source1 and source0 on 'name'
joined_1 = pd.merge(source1, source0, on="name", how="inner")

# Aggregate source2 to get average scores and passing counts per school
agg_scores = source2.groupby("school").agg(
    Average_Math_Score=("math_score", "mean"),
    Average_Reading_Score=("reading_score", "mean"),
    Number_Passing_Math=("math_score", lambda x: (x >= 70).sum()),
    Number_Passing_Reading=("reading_score", lambda x: (x >= 70).sum()),
    School_Size=("school", "count")
).reset_index().rename(columns={"school": "name"})

# Join aggregated scores with joined_1 on 'name'
final_join = pd.merge(joined_1, agg_scores, on="name", how="inner")

# Select and rename columns to match target schema
result = final_join.rename(columns={
    "School ID": "School ID",
    "name": "name",
    "type": "type",
    "size": "size",
    "budget": "budget",
    "Average_Math_Score": "Average Math Score",
    "Average_Reading_Score": "Average Reading Score",
    "Number_Passing_Math": "Number Passing Math",
    "Number_Passing_Reading": "Number Passing Reading",
    "School_Size": "School Size"
})[
    ["School ID", "name", "type", "size", "budget",
     "Average Math Score", "Average Reading Score",
     "Number Passing Math", "Number Passing Reading", "School Size"]
]

# Ensure correct dtypes
result = result.astype({
    "School ID": "int64",
    "name": "string",
    "type": "string",
    "size": "int64",
    "budget": "int64",
    "Average Math Score": "float64",
    "Average Reading Score": "float64",
    "Number Passing Math": "int64",
    "Number Passing Reading": "int64",
    "School Size": "int64"
})

# Save to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)