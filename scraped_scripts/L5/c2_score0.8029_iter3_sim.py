import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_5.csv", index_col=0)

r0 = pd.merge(s3, s1, on="zipcode", suffixes=('_y7', '_boro'))
r0.rename(columns={"businesses": "businesses_y_7", "counts": "counts_y_8", "boro": "boro"}, inplace=True)

r1 = pd.merge(r0, s2, on="zipcode", suffixes=('', '_x5'))
r1.rename(columns={"businesses": "businesses_x_5", "counts": "counts_x_6"}, inplace=True)

r2 = pd.merge(r1, s4, on="zipcode", suffixes=('', '_x'))
r2.rename(columns={"businesses": "businesses_x", "counts": "counts_x"}, inplace=True)

r3 = pd.merge(r2, s0, on="zipcode", suffixes=('', '_s0'))
r3.rename(columns={"businesses": "businesses_y", "counts": "counts_y"}, inplace=True)

r4 = pd.merge(r3, s5, on="zipcode", how="left")
r4.rename(columns={"businesses": "businesses"}, inplace=True)

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

result = r4.groupby(["zipcode", "boro"], as_index=False).agg(agg)

result = result[["zipcode", "businesses_x", "counts_x", "businesses_y", "counts_y",
                 "businesses_x_5", "counts_x_6", "businesses_y_7", "counts_y_8",
                 "boro", "businesses"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_2/target_multisource_mcts.csv", index=False)