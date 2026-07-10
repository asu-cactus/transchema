import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_1.csv", index_col=0)

df = pd.merge(df1, df0, on="Mouse ID", how="inner")

df = df[["Drug", "Timepoint", "Mouse ID"]]

def try_convert_int(series):
    try:
        return series.astype(int)
    except:
        return pd.to_numeric(series, errors='coerce').dropna().astype(int)

df["Timepoint"] = try_convert_int(df["Timepoint"])

# For Mouse ID, source 1 has strings like 'f234', so convert by extracting digits only
def extract_int_from_str(s):
    import re
    m = re.search(r'\d+', s)
    if m:
        return int(m.group())
    else:
        return pd.NA

df["Mouse ID"] = df["Mouse ID"].apply(extract_int_from_str)

df = df.dropna(subset=["Mouse ID", "Timepoint", "Drug"])

df["Mouse ID"] = df["Mouse ID"].astype(int)
df["Timepoint"] = df["Timepoint"].astype(int)
df["Drug"] = df["Drug"].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_8/target_multisource_mcts.csv", index=False)