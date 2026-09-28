import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_5.csv", index_col=0)

# Join s0 and s2 on zipcode
r0 = pd.merge(s0, s2, on="zipcode", suffixes=('_s0', '_s2'))
r0.rename(columns={
    "businesses_s0": "businesses_x_5",  # source0 businesses -> businesses_x_5 (matches target)
    "counts_s0": "counts_x_6",          # source0 counts -> counts_x_6
    "businesses_s2": "businesses_y",    # source2 businesses -> businesses_y
    "counts_s2": "counts_y"              # source2 counts -> counts_y
}, inplace=True)

# Join r0 with s3
r1 = pd.merge(r0, s3, on="zipcode")
r1.rename(columns={
    "businesses": "businesses_y_7",
    "counts": "counts_y_8"
}, inplace=True)

# Join r1 with s4
r2 = pd.merge(r1, s4, on="zipcode")
r2.rename(columns={
    "businesses": "businesses_x",
    "counts": "counts_x"
}, inplace=True)

# Join r2 with s1 (boro info)
r3 = pd.merge(r2, s1, on="zipcode")

# Join r3 with s5 (businesses integer count)
r4 = pd.merge(r3, s5, on="zipcode", how="left")

# Aggregation dictionary
agg = {
    "businesses_x": "first",
    "counts_x": "sum",
    "businesses_y": "first",
    "counts_y": "sum",
    "businesses_x_5": "first",
    "counts_x_6": "sum",
    "businesses_y_7": "first",
    "counts_y_8": "sum",
    "boro": "first",
    "businesses": "sum"
}

result = r4.groupby("zipcode", as_index=False).agg(agg)

# Reorder columns to match target schema exactly
result = result[[
    "zipcode",
    "businesses_x",
    "counts_x",
    "businesses_y",
    "counts_y",
    "businesses_x_5",
    "counts_x_6",
    "businesses_y_7",
    "counts_y_8",
    "boro",
    "businesses"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_2/target_multisource_mcts.csv", index=False)