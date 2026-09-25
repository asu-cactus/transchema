import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_66/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_66/training_1.csv", index_col=0)

df0_agg = df0.groupby("Timepoint").agg({
    "Tumor Volume (mm3)": "mean",
    "Metastatic Sites": "mean"
}).reset_index()

drug_counts = df1.groupby("Drug").size().reset_index(name="count")

timepoints = df0_agg["Timepoint"].unique()

drugs = ['Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol']

data = {"Timepoint": timepoints}
for drug in drugs:
    data[drug] = [0]*len(timepoints)

target_df = pd.DataFrame(data)

target_df = target_df.astype({
    "Timepoint": int,
    "Capomulin": int,
    "Ceftamin": float,
    "Infubinol": int,
    "Ketapril": float,
    "Naftisol": float,
    "Placebo": int,
    "Propriva": int,
    "Ramicane": float,
    "Stelasyn": float,
    "Zoniferol": int
})

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_66/target_multisource_mcts.csv", index=False)