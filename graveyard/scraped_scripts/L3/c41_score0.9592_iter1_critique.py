import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_41/training_1.csv", index_col=0)

# Join on school_name
merged = pd.merge(df0, df1, on="school_name", how="inner")

# Group by school_name
agg = merged.groupby("school_name").agg(
    Total_Students=pd.NamedAgg(column="Student ID", aggfunc="count"),
    Total_School_Budget=pd.NamedAgg(column="budget", aggfunc="first"),
    Average_Math_Score=pd.NamedAgg(column="math_score", aggfunc="mean"),
    Average_Reading_Score=pd.NamedAgg(column="reading_score", aggfunc="mean"),
).reset_index(drop=True)

# Cast types as per target schema
agg["Total_Students"] = agg["Total_Students"].astype(int)
agg["Total_School_Budget"] = agg["Total_School_Budget"].astype(int)
agg["Average_Math_Score"] = agg["Average_Math_Score"].astype(float)
agg["Average_Reading_Score"] = agg["Average_Reading_Score"].astype(float)

# Rename columns to match target schema exactly
agg.columns = ["Total Students", "Total School Budget", "Average Math Score", "Average Reading Score"]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_41/target_multisource_mcts.csv", index=False)