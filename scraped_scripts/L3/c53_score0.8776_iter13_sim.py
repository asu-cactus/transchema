import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_2.csv", index_col=0)

count0 = df0.groupby("B-day")["ID Number"].count()
count1 = df1.groupby("B-day")["ID Number"].count()
count2 = df2.groupby("B-day")["ID Number"].count()

result = pd.DataFrame({
    "B-day": count0.index,
    "ID Number": count0.values,
    "Name_x": count1.reindex(count0.index, fill_value=0).values,
    "Fed_x": count2.reindex(count0.index, fill_value=0).values,
    "Sex_x": count2.reindex(count0.index, fill_value=0).values
})

result["B-day"] = result["B-day"].astype(int)
result["ID Number"] = result["ID Number"].astype(int)
result["Name_x"] = result["Name_x"].astype(int)
result["Fed_x"] = result["Fed_x"].astype(int)
result["Sex_x"] = result["Sex_x"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_53/target_multisource_mcts.csv", index=False)