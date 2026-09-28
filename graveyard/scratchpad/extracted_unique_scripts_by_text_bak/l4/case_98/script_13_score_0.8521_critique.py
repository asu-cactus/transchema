import pandas as pd

# Read both source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_1.csv", index_col=0)

# Join on PassengerId
df_joined = pd.merge(df0, df1, on="PassengerId", suffixes=('_x', '_y'))

# Select and reorder columns to match target schema
result = df_joined[[
    "PassengerId",
    "Survived_x",  # Survived from first source
    "Pclass_x",
    "Name_x",
    "Sex_x",
    "Age_x",
    "SibSp_x",
    "Parch_x",
    "Ticket_x",
    "Fare_x",
    "Cabin_x",
    "Embarked_x",
    "Fare_x",  # Fare_x already selected
    "Fare_y"
]]

# Rename columns to match target schema exactly
result.columns = [
    "PassengerId",
    "Survived",
    "Pclass",
    "Name",
    "Sex",
    "Age",
    "SibSp",
    "Parch",
    "Ticket",
    "Fare",
    "Cabin",
    "Embarked",
    "Fare_x",
    "Fare_y"
]

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)