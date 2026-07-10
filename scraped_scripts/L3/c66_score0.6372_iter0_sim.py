import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_66/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_66/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="Mouse ID")

def count_if(group, drug_name):
    return (group == drug_name).sum()

grouped = df.groupby("Timepoint")["Drug"].agg(
    Capomulin=lambda x: count_if(x, "Capomulin"),
    Ceftamin=lambda x: count_if(x, "Ceftamin"),
    Infubinol=lambda x: count_if(x, "Infubinol"),
    Ketapril=lambda x: count_if(x, "Ketapril"),
    Naftisol=lambda x: count_if(x, "Naftisol"),
    Placebo=lambda x: count_if(x, "Placebo"),
    Propriva=lambda x: count_if(x, "Propriva"),
    Ramicane=lambda x: count_if(x, "Ramicane"),
    Stelasyn=lambda x: count_if(x, "Stelasyn"),
    Zoniferol=lambda x: count_if(x, "Zoniferol"),
).reset_index()

grouped["Timepoint"] = grouped["Timepoint"].astype(int)
grouped["Capomulin"] = grouped["Capomulin"].astype(int)
grouped["Ceftamin"] = grouped["Ceftamin"].astype(float)
grouped["Infubinol"] = grouped["Infubinol"].astype(int)
grouped["Ketapril"] = grouped["Ketapril"].astype(float)
grouped["Naftisol"] = grouped["Naftisol"].astype(float)
grouped["Placebo"] = grouped["Placebo"].astype(int)
grouped["Propriva"] = grouped["Propriva"].astype(int)
grouped["Ramicane"] = grouped["Ramicane"].astype(float)
grouped["Stelasyn"] = grouped["Stelasyn"].astype(float)
grouped["Zoniferol"] = grouped["Zoniferol"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_66/target_multisource_mcts.csv", index=False)