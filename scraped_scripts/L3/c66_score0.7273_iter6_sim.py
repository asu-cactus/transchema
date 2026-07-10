import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_66/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_66/training_1.csv", index_col=0)

agg_df0 = df0.groupby("Timepoint").agg({
    "Metastatic Sites": "sum",
    "Tumor Volume (mm3)": "min",
    "Metastatic Sites": "max"
}).rename(columns={
    "Metastatic Sites": "Metastatic Sites Sum",
    "Tumor Volume (mm3)": "Tumor Volume Min",
    "Metastatic Sites": "Metastatic Sites Max"
})

# The above aggregation with duplicate keys will only keep the last aggregation for "Metastatic Sites" (max).
# We need to do all aggregations separately and then join.

metastatic_sum = df0.groupby("Timepoint")["Metastatic Sites"].sum()
tumor_min = df0.groupby("Timepoint")["Tumor Volume (mm3)"].min()
metastatic_max = df0.groupby("Timepoint")["Metastatic Sites"].max()

agg_df0 = pd.concat([metastatic_sum, tumor_min, metastatic_max], axis=1)
agg_df0.columns = ["Metastatic Sites Sum", "Tumor Volume Min", "Metastatic Sites Max"]
agg_df0 = agg_df0.reset_index()

# Join df0 with df1 on Mouse ID to get Drug info for each Mouse ID
df0_with_drug = pd.merge(df0, df1, on="Mouse ID", how="left")

# Aggregate metastatic sites sum by Timepoint and Drug
agg = df0_with_drug.groupby(["Timepoint", "Drug"])["Metastatic Sites"].sum().reset_index()

# Pivot to get drugs as columns
pivot = agg.pivot(index="Timepoint", columns="Drug", values="Metastatic Sites").fillna(0)

# The target schema drugs columns are:
# ['Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol']

# Ensure all these columns exist in pivot, add missing with 0
target_drugs = ['Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol']
for drug in target_drugs:
    if drug not in pivot.columns:
        pivot[drug] = 0

pivot = pivot[target_drugs].reset_index()

# Cast columns to target types
pivot["Timepoint"] = pivot["Timepoint"].astype(int)
pivot["Capomulin"] = pivot["Capomulin"].astype(int)
pivot["Ceftamin"] = pivot["Ceftamin"].astype(float)
pivot["Infubinol"] = pivot["Infubinol"].astype(int)
pivot["Ketapril"] = pivot["Ketapril"].astype(float)
pivot["Naftisol"] = pivot["Naftisol"].astype(float)
pivot["Placebo"] = pivot["Placebo"].astype(int)
pivot["Propriva"] = pivot["Propriva"].astype(int)
pivot["Ramicane"] = pivot["Ramicane"].astype(float)
pivot["Stelasyn"] = pivot["Stelasyn"].astype(float)
pivot["Zoniferol"] = pivot["Zoniferol"].astype(int)

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_66/target_multisource_mcts.csv", index=False)