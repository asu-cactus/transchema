import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_9.csv", index_col=0)

df = s7.merge(s4, on="2012-12-05", how="inner")
df = df.merge(s5, on="2012-12-05", how="inner")
df = df.merge(s1, on="2012-12-05", how="inner")
df = df.merge(s2, on="2012-12-05", how="inner")
df = df.merge(s3, on="2012-12-05", how="inner")
df = df.merge(s0, on="2012-12-05", how="inner")
df = df.merge(s6, on="2012-12-05", how="inner")
df = df.merge(s8, on="2012-12-05", how="inner")
df = df.merge(s9, on="2012-12-05", how="inner")

# Rename columns to match target schema exactly
# The columns after merge are the key plus all value columns from sources
# The source columns have their original names (the second column in each source)
# We must rename them to the target schema column names in order:
# Target schema: ['2012-12-05': string, '301.0': integer, '0.0075805085': float, '0.0179': float, '6.9': float, '0.17657143': float, '20.3333': float, '0.016157143': float, '242.364': float, '0.1646': float, '0.7268': float]
# Map source to target columns:
# s7: '301.0' (int)
# s4: '0.0075805085' (float)
# s5: '0.0179' (float)
# s1: '0.016157143' (float)
# s2: '0.17657143' (float)
# s3: '6.9' (float)
# s0: '0.7268' (float)
# s6: '242.364' (float)
# s8: '20.3333' (float)
# s9: '0.1646' (float)

df.columns = [
    "2012-12-05",
    "301.0",
    "0.0075805085",
    "0.0179",
    "0.016157143",
    "0.17657143",
    "6.9",
    "0.7268",
    "242.364",
    "20.3333",
    "0.1646"
]

df["2012-12-05"] = df["2012-12-05"].astype(str)
df["301.0"] = pd.to_numeric(df["301.0"], errors='coerce').astype('Int64')
df["0.0075805085"] = pd.to_numeric(df["0.0075805085"], errors='coerce').astype(float)
df["0.0179"] = pd.to_numeric(df["0.0179"], errors='coerce').astype(float)
df["6.9"] = pd.to_numeric(df["6.9"], errors='coerce').astype(float)
df["0.17657143"] = pd.to_numeric(df["0.17657143"], errors='coerce').astype(float)
df["20.3333"] = pd.to_numeric(df["20.3333"], errors='coerce').astype(float)
df["0.016157143"] = pd.to_numeric(df["0.016157143"], errors='coerce').astype(float)
df["242.364"] = pd.to_numeric(df["242.364"], errors='coerce').astype(float)
df["0.1646"] = pd.to_numeric(df["0.1646"], errors='coerce').astype(float)
df["0.7268"] = pd.to_numeric(df["0.7268"], errors='coerce').astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_11/target_multisource_mcts.csv", index=False)