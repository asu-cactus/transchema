import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

join_01 = pd.merge(s0, s1, on=["SubjectId", "Split", "Subject"], suffixes=('_0', '_1'))
join_012 = pd.merge(join_01, s2, on=["SubjectId", "Split", "Subject"])
join_012 = join_012.rename(columns={col: col + '_2' for col in s2.columns if col not in ["SubjectId", "Split", "Subject"]})
join_012_3 = pd.merge(join_012, s3, on=["SubjectId", "Split", "Subject"])
join_012_3 = join_012_3.rename(columns={col: col + '_3' for col in s3.columns if col not in ["SubjectId", "Split", "Subject"]})

cols = ["SubjectId", "Split", "Subject",
        "PA_0", "AB_0", "H_0", "TB_0", "BB_0", "SF_0", "HBP_0",
        "PA_1", "AB_1", "H_1", "TB_1", "BB_1", "SF_1", "HBP_1",
        "PA_2", "AB_2", "H_2", "TB_2", "BB_2", "SF_2", "HBP_2",
        "PA_3", "AB_3", "H_3", "TB_3", "BB_3", "SF_3", "HBP_3"]

df = join_012_3[cols]

df = df.rename(columns={
    "PA_0": "PA",
    "AB_0": "AB",
    "H_0": "H",
    "TB_0": "TB",
    "BB_0": "BB",
    "SF_0": "SF",
    "HBP_0": "HBP"
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv")