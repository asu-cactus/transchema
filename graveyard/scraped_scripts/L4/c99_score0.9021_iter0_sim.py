import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

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
grouped["Fare_y"] = 10.5

grouped = grouped.astype({
    "PassengerId": "int64",
    "Survived": "int64",
    "Pclass": "int64",
    "Name": "string",
    "Sex": "string",
    "Age": "float64",
    "SibSp": "int64",
    "Parch": "int64",
    "Ticket": "string",
    "Fare": "float64",
    "Cabin": "string",
    "Embarked": "string",
    "Fare_x": "float64",
    "Fare_y": "float64"
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)