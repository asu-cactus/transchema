import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_4.csv", index_col=0)

agg1 = df1.groupby("age_grp", dropna=False)["Count"].sum()
agg3 = df3.groupby("age_grp", dropna=False)["Count"].sum()
agg0_rate = df0.groupby("age_grp", dropna=False)["Rate"].mean()
agg2_rate = df2.groupby("age_grp", dropna=False)["Rate"].mean()
agg4_rate = df4.groupby("age_grp", dropna=False)["Rate"].mean()

agg_df = pd.DataFrame({
    "age_grp": agg1.index,
    "Count_1": agg1.values,
    "Count_3": agg3.reindex(agg1.index).values,
    "Rate_0": agg0_rate.reindex(agg1.index).values,
    "Rate_2": agg2_rate.reindex(agg1.index).values,
    "Rate_4": agg4_rate.reindex(agg1.index).values,
})

agg_df["Count"] = agg_df["Count_1"] + agg_df["Count_3"]
agg_df["Rate"] = agg_df[["Rate_0", "Rate_2", "Rate_4"]].mean(axis=1)

# Prepare Notes and Statistics columns from df1 and df0 respectively
# For Notes: take the most frequent non-null Notes per age_grp from df1
notes = df1.groupby("age_grp")["Notes"].agg(lambda x: x.dropna().mode().iloc[0] if not x.dropna().empty else pd.NA)
# For Statistics: take the most frequent non-null Statistics per age_grp from df0
statistics = df0.groupby("age_grp")["Statistics"].agg(lambda x: x.dropna().mode().iloc[0] if not x.dropna().empty else pd.NA)

agg_df = agg_df.set_index("age_grp")
agg_df["Notes"] = notes.reindex(agg_df.index)
agg_df["Statistics"] = statistics.reindex(agg_df.index)

result = agg_df.reset_index()[["age_grp", "Count", "Notes", "Rate", "Statistics"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)