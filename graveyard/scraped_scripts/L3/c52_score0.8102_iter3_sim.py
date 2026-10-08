import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_3.csv", index_col=0)

j1 = pd.merge(s1, s2, on="zipcode", suffixes=("_x", "_y"))
j2 = pd.merge(j1, s0, on="zipcode")
j3 = pd.merge(j2, s3, on="zipcode", suffixes=("_5", "_7"))

result = j3.rename(columns={
    "businesses_x": "businesses_x",
    "counts_x": "counts_x",
    "businesses_y": "businesses_y",
    "counts_y": "counts_y",
    "businesses_5": "businesses_x_5",
    "counts_6": "counts_x_6",
    "businesses_7": "businesses_y_7",
    "counts": "counts_y_8"
})

# After merges, columns from s0 and s3 have no suffix for s0 and suffix _7 for s3.
# But s0 columns are 'businesses' and 'counts' without suffix, s3 columns have suffix _7.
# So rename accordingly:
result = result.rename(columns={
    "businesses": "businesses_x_5",
    "counts": "counts_x_6",
    "businesses_7": "businesses_y_7",
    "counts_7": "counts_y_8"
})

# The above rename may conflict because after merge with s3, suffixes are _5 and _7 for s0 and s3 respectively.
# But in the second merge, suffixes were not set, so s0 columns remain as 'businesses' and 'counts'.
# In the third merge, suffixes=('_5', '_7') are applied to the right and left tables respectively.
# So s0 columns get suffix _5, s3 columns get suffix _7.
# So the columns after all merges are:
# zipcode
# businesses_x (from s1)
# counts_x (from s1)
# businesses_y (from s2)
# counts_y (from s2)
# businesses_5 (from s0)
# counts_5 (from s0)
# businesses_7 (from s3)
# counts_7 (from s3)
# We want to rename:
# businesses_5 -> businesses_x_5
# counts_5 -> counts_x_6
# businesses_7 -> businesses_y_7
# counts_7 -> counts_y_8

result = result.rename(columns={
    "businesses_5": "businesses_x_5",
    "counts_5": "counts_x_6",
    "businesses_7": "businesses_y_7",
    "counts_7": "counts_y_8"
})

result = result[[
    "zipcode",
    "businesses_x",
    "counts_x",
    "businesses_y",
    "counts_y",
    "businesses_x_5",
    "counts_x_6",
    "businesses_y_7",
    "counts_y_8"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_52/target_multisource_mcts.csv")