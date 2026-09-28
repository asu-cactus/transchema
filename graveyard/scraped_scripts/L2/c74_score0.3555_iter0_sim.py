import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_74/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_74/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

result = merged[["Drug", "Timepoint", "Mouse ID"]].copy()
result["Timepoint"] = result["Timepoint"].astype(int)

def try_int_conversion(val):
    try:
        return int(val)
    except:
        return val

result["Mouse ID"] = result["Mouse ID"].apply(try_int_conversion)
# If Mouse ID cannot be converted to int, keep original string (as no instruction to fill or drop)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_74/target_multisource_mcts.csv", index=False)