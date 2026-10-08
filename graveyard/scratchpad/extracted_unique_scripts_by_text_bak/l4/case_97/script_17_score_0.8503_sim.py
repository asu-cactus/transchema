import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# The source has columns: ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked']
# The target has two additional columns: Fare_x (float), Fare_y (integer)
# The partial plan suggests UNPIVOT then GROUP_BY on Name.
# Since only one source table, and target has Fare_x and Fare_y, likely Fare_x and Fare_y come from unpivoting Fare or from joining multiple sources.
# But only one source is given, so we must create Fare_x and Fare_y from Fare column by unpivoting or splitting.

# Step 1: UNPIVOT - but we have only one source table, no multiple fare columns.
# Possibly Fare_x and Fare_y come from unpivoting Fare into two columns: Fare_x (float) and Fare_y (integer).
# Let's create a DataFrame with Fare_x = Fare (float), Fare_y = Fare cast to int.

df = df0.copy()
df['Fare_x'] = df['Fare'].astype(float)
df['Fare_y'] = df['Fare'].fillna(0).astype(int)

# The target schema columns:
# ['PassengerId': int, 'Survived': int, 'Pclass': int, 'Name': str, 'Sex': str, 'Age': float,
#  'SibSp': int, 'Parch': int, 'Ticket': str, 'Fare': float, 'Cabin': str, 'Embarked': str,
#  'Fare_x': float, 'Fare_y': int]

# Ensure types match target schema:
df['PassengerId'] = df['PassengerId'].astype(int)
df['Survived'] = df['Survived'].astype(int)
df['Pclass'] = df['Pclass'].astype(int)
df['Name'] = df['Name'].astype(str)
df['Sex'] = df['Sex'].astype(str)
df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
df['SibSp'] = df['SibSp'].astype(int)
df['Parch'] = df['Parch'].astype(int)
df['Ticket'] = df['Ticket'].astype(str)
df['Fare'] = pd.to_numeric(df['Fare'], errors='coerce')
df['Cabin'] = df['Cabin'].astype(str)
df['Embarked'] = df['Embarked'].astype(str)
df['Fare_x'] = df['Fare_x'].astype(float)
df['Fare_y'] = df['Fare_y'].astype(int)

# Group by Name as per partial plan
# The target examples show no aggregation columns except Fare_x and Fare_y which we already set.
# Grouping by Name means aggregating other columns by some aggregation.
# But PassengerId is unique per row, so grouping by Name may produce multiple PassengerIds per Name.
# To keep consistent, aggregate numeric columns by mean or first, and for categorical columns take first.

agg_dict = {
    'PassengerId': 'first',
    'Survived': 'first',
    'Pclass': 'first',
    'Sex': 'first',
    'Age': 'mean',
    'SibSp': 'first',
    'Parch': 'first',
    'Ticket': 'first',
    'Fare': 'mean',
    'Cabin': 'first',
    'Embarked': 'first',
    'Fare_x': 'mean',
    'Fare_y': 'mean'
}

df_grouped = df.groupby('Name', as_index=False).agg(agg_dict)

# Cast Fare_y back to int after mean aggregation
df_grouped['Fare_y'] = df_grouped['Fare_y'].round().astype(int)

# Reorder columns to match target schema
final_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
df_final = df_grouped[final_cols]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)