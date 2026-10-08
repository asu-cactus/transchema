import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

# Join the table with itself on PassengerId to get Fare_x and Fare_y
# Use suffixes to distinguish Fare columns
df_joined = df0.merge(df0, on="PassengerId", suffixes=('_x', '_y'), how='inner')

# Select columns as per target schema
result = df_joined[[
    "PassengerId",
    "Survived_x",  # Survived from left table
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
    "Fare_x",  # Fare_x again (same as above)
    "Fare_y"   # Fare_y from right table
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

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)