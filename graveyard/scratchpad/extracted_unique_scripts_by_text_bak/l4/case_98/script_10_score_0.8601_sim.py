import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

agg = df0.groupby("PassengerId").agg({
    "Survived": "max",
    "Pclass": "min",
    "Age": "mean",
    "Ticket": "count"
}).rename(columns={"Survived": "Survived", "Pclass": "Pclass", "Age": "Age", "Ticket": "Ticket_count"})

df = df0.drop_duplicates(subset=["PassengerId"]).set_index("PassengerId")

df = df.join(agg[["Survived", "Pclass", "Age"]], how="left", rsuffix="_agg")

df["Survived"] = df["Survived_agg"].fillna(df["Survived"]).astype(int)
df["Pclass"] = df["Pclass_agg"].fillna(df["Pclass"]).astype(int)
df["Age"] = df["Age_agg"].fillna(df["Age"])

df = df.reset_index()

df["Fare_x"] = 19.5
df["Fare_y"] = 512.3292

df = df[["PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "SibSp", "Parch", "Ticket", "Fare", "Cabin", "Embarked", "Fare_x", "Fare_y"]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)