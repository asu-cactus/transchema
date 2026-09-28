import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_93/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID")

agg = merged.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).agg({
    "Timepoint": "mean",
    "Tumor Volume (mm3)": "mean",
    "Metastatic Sites": "sum"
})

agg["Timepoint"] = agg["Timepoint"].round().astype(int)
agg["Mouse ID"] = agg["Mouse ID"].astype(str)
agg["Drug"] = agg["Drug"].astype(str)

result = agg[["Drug", "Timepoint", "Mouse ID"]].copy()
result["Mouse ID"] = result["Mouse ID"].apply(lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else 0)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_93/target_multisource_mcts.csv", index=False)