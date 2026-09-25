import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_31/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_31/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_31/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_31/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_31/training_4.csv", index_col=0)

# Concatenate all source tables (union)
df = pd.concat([s0, s1, s2, s3, s4], ignore_index=True)

# Fix data types to match target schema
df["GEO.id"] = df["GEO.id"].astype(str)
df["GEO.id2"] = pd.to_numeric(df["GEO.id2"], errors='coerce').fillna(0).astype(int)
# The target schema says GEO.display-label is integer, but source has string "ZCTA5 91932" etc.
# We must convert GEO.display-label to integer. The source examples show "ZCTA5 91932" (string).
# The target example shows GEO.display-label as integer (e.g., 5).
# This suggests GEO.display-label is actually an integer code, but source has string labels.
# We need to convert GEO.display-label to integer by extracting the numeric part or mapping.
# Since the source GEO.display-label is "ZCTA5 91932" (string), we can try to extract the numeric part after "ZCTA5 ".
# Extract the numeric part after "ZCTA5 " and convert to int.
df["GEO.display-label"] = df["GEO.display-label"].str.extract(r'(\d+)').fillna(0).astype(int)

df["HD01_VD01"] = pd.to_numeric(df["HD01_VD01"], errors='coerce').fillna(0).astype(int)
df["HD02_VD01"] = pd.to_numeric(df["HD02_VD01"], errors='coerce').fillna(0).astype(int)
df["Year"] = pd.to_numeric(df["Year"], errors='coerce').fillna(0).astype(int)

# Select columns in target schema order
df = df[["GEO.id", "GEO.id2", "GEO.display-label", "HD01_VD01", "HD02_VD01", "Year"]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_31/target_multisource_mcts.csv", index=False)