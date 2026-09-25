import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# Join the table with itself on PassengerId to produce Fare_x and Fare_y columns
df_joined = df0.merge(df0, on="PassengerId", suffixes=("", "_y"))

# Rename columns to match target schema
# Fare_x is the original Fare (float)
# Fare_y is the integer cast of Fare from the joined table (Fare_y)
df_joined["Fare_x"] = df_joined["Fare"]
df_joined["Fare_y"] = df_joined["Fare_y"].astype("Int64")  # Use nullable integer dtype to allow NaNs if any

# Select columns in the exact order of target schema
df_out = df_joined[
    [
        "PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "SibSp", "Parch",
        "Ticket", "Fare", "Cabin", "Embarked", "Fare_x", "Fare_y"
    ]
]

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)