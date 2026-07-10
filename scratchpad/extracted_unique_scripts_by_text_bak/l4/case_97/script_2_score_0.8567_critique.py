import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# Add Fare_x as mean Fare from df0
fare_x_value = df0["Fare"].mean()

# Add Fare_y as count of rows (integer)
fare_y_value = len(df0)

df0["Fare_x"] = fare_x_value
df0["Fare_y"] = fare_y_value

df0 = df0[[
    "PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "SibSp", "Parch",
    "Ticket", "Fare", "Cabin", "Embarked", "Fare_x", "Fare_y"
]]

df0.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)