import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

s0_renamed = s0.rename(columns={"m1403": "m1403"})
s2_renamed = s2.rename(columns={"m1401": "m1401"})
s3_renamed = s3.rename(columns={"m1402": "m1402"})
s4_renamed = s4.rename(columns={"m1404": "m1404"})

# Add missing columns with NaN to each to align columns for union
cols = ['County', 'm1401', 'm1402', 'm1403', 'm1404']

def add_missing_cols(df, cols):
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df[cols]

df0 = add_missing_cols(s0_renamed, cols)
df2 = add_missing_cols(s2_renamed, cols)
df3 = add_missing_cols(s3_renamed, cols)
df4 = add_missing_cols(s4_renamed, cols)

union_result = pd.concat([df0, df2, df3, df4], ignore_index=True)

result = union_result.merge(s1, on="County", how="outer")

result = result[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv", index=False)