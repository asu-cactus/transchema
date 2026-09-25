import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on school_name
merged = pd.merge(df0, df1, on="school_name", how="inner")

# Group by school_name and type (which corresponds to 'a' in target)
agg = merged.groupby(["school_name", "type"]).agg(
    b = ("size", "sum"),
    c = ("budget", "sum"),
    d = ("reading_score", "mean"),
    e = ("math_score", "mean")
).reset_index()

# Rename 'type' to 'a' to match target schema
agg = agg.rename(columns={"type": "a"})

# Ensure correct types
agg["b"] = agg["b"].astype(int)
agg["c"] = agg["c"].astype(int)
agg["d"] = agg["d"].astype(float)
agg["e"] = agg["e"].astype(float)
agg["a"] = agg["a"].astype(str)
agg["school_name"] = agg["school_name"].astype(str)

# Reorder columns to match target schema
result = agg[["school_name", "a", "b", "c", "d", "e"]]

result.to_csv(target_path, index=False)