import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_77/training_1.csv", index_col=0)

# Join on school_name
df_joined = pd.merge(df0, df1, on="school_name", how="inner")

# Group by school_name and count number of students (Student ID)
agg = df_joined.groupby("school_name", as_index=False)["Student ID"].count()

# Rename count column to reading_score as per target schema
agg.columns = ["school_name", "reading_score"]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_77/target_multisource_mcts.csv", index=False)