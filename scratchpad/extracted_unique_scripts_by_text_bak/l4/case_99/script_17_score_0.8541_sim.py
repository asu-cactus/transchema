import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

agg = df0.groupby("PassengerId").agg(
    Ticket_count=("Ticket", "count"),
    Fare_x=("Fare", "max"),
    Age_min=("Age", "min")
).reset_index()

# The target schema columns:
# ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

# The source has all columns except Fare_x and Fare_y.
# We have Fare_x from aggregation (max Fare per PassengerId).
# We do not have Fare_y in source, but target examples show Fare_y as a float column.
# The partial plan suggests Fare_x and Fare_y are derived from aggregations.
# Since only one source is given, Fare_y can be the min Fare per PassengerId (or another aggregation).
# The partial plan aggregates Fare max only, but target has Fare_x and Fare_y.
# We can add Fare_y as min Fare per PassengerId (or mean Fare).
# Also, the aggregation includes min Age, but target Age is float and can be taken from source directly.
# Since PassengerId is unique in source (likely), we can merge aggregated columns back to source.

agg_extra = df0.groupby("PassengerId").agg(
    Fare_y=("Fare", "min")
).reset_index()

agg_all = pd.merge(agg, agg_extra, on="PassengerId")

# Merge aggregated columns back to original df0 on PassengerId
df_merged = pd.merge(df0, agg_all[["PassengerId", "Fare_x", "Fare_y"]], on="PassengerId", how="left")

# Ensure columns are in target order
target_columns = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

df_final = df_merged[target_columns]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)