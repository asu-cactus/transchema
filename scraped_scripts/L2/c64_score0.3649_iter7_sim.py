import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_64/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_64/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_64/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(df1, df0, on="Mouse ID")

pivoted = merged.pivot_table(index=["Drug", "Mouse ID"], columns="Timepoint", values="Tumor Volume (mm3)").reset_index()

pivoted_long = pivoted.melt(id_vars=["Drug", "Mouse ID"], var_name="Timepoint", value_name="Tumor Volume (mm3)")

result = pivoted_long[["Drug", "Timepoint", "Mouse ID"]]
result["Timepoint"] = result["Timepoint"].astype("int64")

result.to_csv(target_path, index=False)