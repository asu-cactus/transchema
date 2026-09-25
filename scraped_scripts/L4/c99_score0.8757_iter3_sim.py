import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

# The target schema has all columns of source plus Fare_x and Fare_y.
# Since only one source table is given, and target has Fare_x and Fare_y,
# these likely come from pivoting Fare by some category.
# The partial plan suggests PIVOT and GROUP_BY on Name.

# We pivot Fare by 'Sex' to get Fare_x and Fare_y (assuming Fare_x = Fare for male, Fare_y = Fare for female)
# But target examples show Fare_x and Fare_y with float values, different from Fare.
# Since only one source, we try pivot Fare by Sex, grouping by all other columns except Fare.

# Prepare for pivot: keep all columns except Fare, then pivot Fare by Sex.
# Group by all columns except Fare and Sex, then pivot Fare by Sex.

group_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Age', 'SibSp', 'Parch', 'Ticket', 'Cabin', 'Embarked', 'Sex']
# We will pivot Fare by Sex, so Sex must be in index or columns.

# Pivot Fare by Sex, so we need to set index as all columns except Fare and Sex, then pivot Fare by Sex.
# But Sex is the pivot column, so it will become columns.

# Set index as all columns except Fare and Sex
index_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Age', 'SibSp', 'Parch', 'Ticket', 'Cabin', 'Embarked']

pivot_df = df0.pivot_table(index=index_cols, columns='Sex', values='Fare', aggfunc='first').reset_index()

# Rename columns to Fare_x and Fare_y
# From target examples, Fare_x and Fare_y are floats, presumably Fare for male and female respectively.
# We map male -> Fare_x, female -> Fare_y
pivot_df = pivot_df.rename(columns={'male': 'Fare_x', 'female': 'Fare_y'})

# Now merge pivot_df with original df0 on index_cols to get all other columns including Fare (original Fare)
# But pivot_df already has index_cols and Fare_x, Fare_y
# We want to keep all columns from index_cols plus Fare_x, Fare_y plus original Fare and Sex

# The original df0 has Sex and Fare columns, but pivot_df has Fare_x and Fare_y instead of Fare and Sex
# We want to keep Sex and Fare columns as in target schema, plus Fare_x and Fare_y

# Merge df0 with pivot_df on index_cols
result = pd.merge(df0, pivot_df, on=index_cols, how='left')

# Reorder columns to match target schema:
# ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

result = result[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

# Ensure data types match target schema
result['PassengerId'] = result['PassengerId'].astype(int)
result['Survived'] = result['Survived'].astype(int)
result['Pclass'] = result['Pclass'].astype(int)
result['Name'] = result['Name'].astype(str)
result['Sex'] = result['Sex'].astype(str)
result['Age'] = pd.to_numeric(result['Age'], errors='coerce')
result['SibSp'] = result['SibSp'].astype(int)
result['Parch'] = result['Parch'].astype(int)
result['Ticket'] = result['Ticket'].astype(str)
result['Fare'] = pd.to_numeric(result['Fare'], errors='coerce')
result['Cabin'] = result['Cabin'].astype(str)
result['Embarked'] = result['Embarked'].astype(str)
result['Fare_x'] = pd.to_numeric(result['Fare_x'], errors='coerce')
result['Fare_y'] = pd.to_numeric(result['Fare_y'], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)