import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

df_grouped = df0.groupby("PassengerId", as_index=False).agg({
    "Survived": "first",
    "Pclass": "first",
    "Name": "first",
    "Sex": "first",
    "Age": "first",
    "SibSp": "first",
    "Parch": "first",
    "Ticket": "first",
    "Fare": "first",
    "Cabin": "first",
    "Embarked": "first"
})

df_grouped["Fare_x"] = df_grouped["Fare"].astype(float)
df_grouped["Fare_y"] = df_grouped["Fare"].astype(int)

df_grouped = df_grouped[[
    "PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "SibSp", "Parch",
    "Ticket", "Fare", "Cabin", "Embarked", "Fare_x", "Fare_y"
]]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)