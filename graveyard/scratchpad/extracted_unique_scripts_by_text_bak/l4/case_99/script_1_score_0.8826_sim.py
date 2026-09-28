import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

# The partial plan suggests PIVOT then UNION on Source4_99_0 only.
# Since only one source table is given, UNION is trivial (just that table).
# The target schema has extra columns Fare_x and Fare_y which do not exist in source.
# These likely come from a pivot operation on Fare by some categorical column.
# We need to identify the pivot key and values.

# Inspect columns: Fare_x and Fare_y suggest pivoting Fare by some column with two distinct values.
# The only categorical columns in source that might be used for pivoting Fare are 'Embarked' or 'Pclass' or 'Sex'.
# From target examples, Fare_x and Fare_y have values like 25.100682 and 10.5 or 44.033212 and 19.5.
# Possibly Fare_x and Fare_y correspond to Fare for two different categories of a column.

# Let's try pivoting Fare by 'Pclass' (which has values 1,2,3) or 'Embarked' (S,C,Q).
# Since only two Fare columns exist, likely pivot by 'Pclass' with two classes or by 'Sex' (male/female).
# 'Sex' has two values: male, female. Let's pivot Fare by Sex.

pivot_df = df0.pivot(index='PassengerId', columns='Sex', values='Fare').reset_index()
pivot_df.columns.name = None
pivot_df = pivot_df.rename(columns={'male': 'Fare_x', 'female': 'Fare_y'})

# Merge pivoted fares back to original df0 on PassengerId
df = pd.merge(df0, pivot_df, on='PassengerId', how='left')

# Reorder and cast columns to match target schema
df = df[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

df = df.astype({
    'PassengerId': 'int64',
    'Survived': 'int64',
    'Pclass': 'int64',
    'Name': 'string',
    'Sex': 'string',
    'Age': 'float64',
    'SibSp': 'int64',
    'Parch': 'int64',
    'Ticket': 'string',
    'Fare': 'float64',
    'Cabin': 'string',
    'Embarked': 'string',
    'Fare_x': 'float64',
    'Fare_y': 'float64'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)