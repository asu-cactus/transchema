import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="school_name", how="inner")

agg = merged.groupby("school_name").agg(
    a=pd.NamedAgg(column="type", aggfunc="first"),
    b=pd.NamedAgg(column="size", aggfunc="sum"),
    c=pd.NamedAgg(column="reading_score", aggfunc="sum"),
    d=pd.NamedAgg(column="reading_score", aggfunc="mean"),
    e=pd.NamedAgg(column="math_score", aggfunc="mean"),
).reset_index()

agg["a"] = agg["a"].astype(str)
agg["b"] = agg["b"].astype(int)
agg["c"] = agg["c"].astype(int)
agg["d"] = agg["d"].astype(float)
agg["e"] = agg["e"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)