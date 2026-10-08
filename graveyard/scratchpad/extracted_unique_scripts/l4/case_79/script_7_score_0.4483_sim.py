import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

join_result = pd.merge(s0, s1, on="hero", suffixes=('_0', '_1'))

union_234 = pd.concat([s2, s3, s4], ignore_index=True)

# Prepare join_result to have same schema as union_234 for union:
# We have columns: hero, disadvantage_0, winrate_0, matches_0, disadvantage_1, winrate_1, matches_1
# We need to combine disadvantage, winrate, matches from both sides into one set of columns by averaging weighted by matches

def weighted_avg(row, col):
    v0 = row[f"{col}_0"]
    v1 = row[f"{col}_1"]
    m0 = row["matches_0"]
    m1 = row["matches_1"]
    if pd.isna(v0) and pd.isna(v1):
        return pd.NA
    if pd.isna(v0):
        return v1
    if pd.isna(v1):
        return v0
    return (v0 * m0 + v1 * m1) / (m0 + m1) if (m0 + m1) > 0 else (v0 + v1) / 2

join_result["disadvantage"] = join_result.apply(lambda r: weighted_avg(r, "disadvantage"), axis=1)
join_result["winrate"] = join_result.apply(lambda r: weighted_avg(r, "winrate"), axis=1)
join_result["matches"] = join_result["matches_0"] + join_result["matches_1"]

join_result = join_result[["hero", "disadvantage", "winrate", "matches"]]

combined = pd.concat([join_result, union_234], ignore_index=True)

agg = combined.groupby("hero", as_index=False).agg({
    "disadvantage": "mean",
    "winrate": "mean",
    "matches": "sum"
})

agg["disadvantage"] = agg["disadvantage"].astype(float)
agg["winrate"] = agg["winrate"].astype(float)
agg["matches"] = agg["matches"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)