import pandas as pd

# Read the single source table twice to simulate two sources for join
df_left = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)
df_right = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# Rename columns in right to distinguish Fare column for Fare_y
df_right_renamed = df_right.rename(columns={"Fare": "Fare_y"})

# Join on PassengerId (primary key)
df_joined = pd.merge(df_left, df_right_renamed, on="PassengerId", how="inner", suffixes=("", "_right"))

# Create Fare_x as float from left Fare, Fare_y as int from right Fare_y
df_joined["Fare_x"] = df_joined["Fare"].astype(float)
df_joined["Fare_y"] = df_joined["Fare_y"].astype(int)

# Group by PassengerId (unique key) and aggregate other columns by first
df_final = df_joined.groupby("PassengerId", as_index=False).agg({
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
    "Embarked": "first",
    "Fare_x": "first",
    "Fare_y": "first"
})

# Reorder columns to match target schema exactly
df_final = df_final[[
    "PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "SibSp", "Parch",
    "Ticket", "Fare", "Cabin", "Embarked", "Fare_x", "Fare_y"
]]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)