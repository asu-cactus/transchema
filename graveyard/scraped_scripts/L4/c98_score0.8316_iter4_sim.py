import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

agg = df0.groupby("PassengerId").agg({
    "Survived": "max",
    "Pclass": "min",
    "Age": "mean",
    "Ticket": "count"
}).rename(columns={"Survived": "Survived", "Pclass": "Pclass", "Age": "Age", "Ticket": "Ticket_count"})

# The target schema requires all columns from source plus Fare_x and Fare_y.
# Since only one source table is given, and no other source tables to join or union,
# we assume Fare_x and Fare_y are not derivable from source and should be set as NaN.

# Merge aggregated columns back to original to get other columns (Name, Sex, SibSp, Parch, Ticket, Fare, Cabin, Embarked)
# Use PassengerId as key
df_merged = pd.merge(df0.drop(columns=["Survived", "Pclass", "Age", "Ticket"]), agg, on="PassengerId", how="left")

# Rename columns to match target schema
df_merged = df_merged.rename(columns={
    "Survived": "Survived",
    "Pclass": "Pclass",
    "Age": "Age",
    "Ticket_count": "Ticket"
})

# Reorder columns to target schema order
target_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

# Add Fare_x and Fare_y as NaN columns (float)
df_merged["Fare_x"] = pd.NA
df_merged["Fare_y"] = pd.NA

df_final = df_merged[target_cols]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)