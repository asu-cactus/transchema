import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

agg = df0.groupby("PassengerId").agg({
    "Survived": "min",
    "Pclass": "max",
    "SibSp": "sum",
    "Parch": "mean"
}).reset_index()

agg["Parch"] = agg["Parch"].round().astype(int)

df_merged = pd.merge(agg, df0.drop(columns=["Survived", "Pclass", "SibSp", "Parch"]).drop_duplicates(subset=["PassengerId"]), on="PassengerId", how="left")

df_merged["Fare_x"] = df0["Fare"].mean()
df_merged["Fare_y"] = 171

df_merged = df_merged[[
    "PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "SibSp", "Parch",
    "Ticket", "Fare", "Cabin", "Embarked", "Fare_x", "Fare_y"
]]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)