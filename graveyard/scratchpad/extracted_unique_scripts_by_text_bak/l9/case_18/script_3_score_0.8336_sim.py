import pandas as pd

Source9_18_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_0.csv", index_col=0)
Source9_18_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_1.csv", index_col=0)
Source9_18_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_2.csv", index_col=0)
Source9_18_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_3.csv", index_col=0)
Source9_18_4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_4.csv", index_col=0)
Source9_18_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_5.csv", index_col=0)
Source9_18_6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_6.csv", index_col=0)
Source9_18_7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_7.csv", index_col=0)
Source9_18_8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_8.csv", index_col=0)
Source9_18_9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_9.csv", index_col=0)

j1 = pd.merge(Source9_18_9, Source9_18_1, on="zipcode", suffixes=('_x', '_y'))
j2 = pd.merge(j1, Source9_18_3, on="zipcode", suffixes=('', '_x_5'))
j2 = j2.rename(columns={"businesses": "businesses_x_5", "counts": "counts_x_6"})
j3 = pd.merge(j2, Source9_18_7, on="zipcode", suffixes=('', '_y_7'))
j3 = j3.rename(columns={"businesses": "businesses_y_7", "counts": "counts_y_8"})
j4 = pd.merge(j3, Source9_18_4, on="zipcode")
j5 = pd.merge(j4, Source9_18_6, on="zipcode")
j5 = j5.rename(columns={"counts": "counts_x_10"})
j6 = pd.merge(j5, Source9_18_8, on="zipcode")
j6 = j6.rename(columns={"counts": "counts_y_11"})
j7 = pd.merge(j6, Source9_18_2, on="zipcode")
j8 = pd.merge(j7, Source9_18_0, on="zipcode")
j9 = pd.merge(j8, Source9_18_5, on="zipcode")

Target9_18 = j9.rename(columns={
    "businesses_x": "businesses_x",
    "counts_x": "counts_x",
    "businesses_y": "businesses_y",
    "counts_y": "counts_y",
    "boro": "boro",
    "indicator": "indicator",
    "counts": "counts",
    "total_crime": "total_crime",
    "violation": "violation",
    "misdemeanor": "misdemeanor",
    "felony": "felony",
    "theft": "theft",
    "assault": "assault",
    "harassment": "harassment"
})

Target9_18 = Target9_18[[
    "zipcode",
    "businesses_x", "counts_x",
    "businesses_y", "counts_y",
    "businesses_x_5", "counts_x_6",
    "businesses_y_7", "counts_y_8",
    "boro",
    "counts_x_10", "counts_y_11",
    "indicator",
    "counts",
    "total_crime",
    "violation",
    "misdemeanor",
    "felony",
    "theft",
    "assault",
    "harassment"
]]

Target9_18.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv")