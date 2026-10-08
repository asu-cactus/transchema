import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

agg_df = df0.groupby("PassengerId").agg({
    "Survived": "max",
    "Pclass": "min",
    "Age": "mean",
    "SibSp": "sum",
    "Parch": "sum",
    "Fare": "mean"
}).reset_index()

agg_df["Survived"] = agg_df["Survived"].astype("Int64")
agg_df["Pclass"] = agg_df["Pclass"].astype("Int64")
agg_df["SibSp"] = agg_df["SibSp"].astype("Int64")
agg_df["Parch"] = agg_df["Parch"].astype("Int64")

df0_unique = df0.drop_duplicates(subset=["PassengerId"]).set_index("PassengerId")

result = agg_df.set_index("PassengerId").join(df0_unique[["Name", "Sex", "Ticket", "Cabin", "Embarked"]])

result["Age"] = agg_df["Age"]
result["Fare"] = agg_df["Fare"]

result["Fare_x"] = agg_df["Fare"]
result["Fare_y"] = df0_unique["Fare"]

result = result.reset_index()

result = result[[
    "PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "SibSp", "Parch",
    "Ticket", "Fare", "Cabin", "Embarked", "Fare_x", "Fare_y"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)