import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

grouped = df0.groupby("Name", as_index=False).agg({
    "PassengerId": "first",
    "Survived": "first",
    "Pclass": "first",
    "Sex": "first",
    "Age": "first",
    "SibSp": "first",
    "Parch": "first",
    "Ticket": "first",
    "Fare": "first",
    "Cabin": "first",
    "Embarked": "first"
})

grouped["Fare_x"] = grouped["Fare"]
grouped["Fare_y"] = grouped["Fare"].astype(int)

grouped = grouped[[
    "PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "SibSp", "Parch",
    "Ticket", "Fare", "Cabin", "Embarked", "Fare_x", "Fare_y"
]]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)