import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# First PIVOT: create Fare_x and Fare_y from Fare by pivoting on some categorical variable
# Since only one source table, and target has Fare_x (float) and Fare_y (int), 
# we guess Fare_x and Fare_y come from pivoting Fare by Embarked or Cabin or similar.
# But source has no repeated PassengerId, so pivoting on PassengerId won't work.
# The target has Fare_x (float) and Fare_y (int), Fare_y looks like an integer version of Fare or a related column.

# The partial plan says two PIVOTs, so likely we pivot twice on different columns to get Fare_x and Fare_y.

# Step 1: Create Fare_x by pivoting Fare on Embarked (S, C, Q) or Cabin or Sex or Pclass
# But target has Fare_x as float and Fare_y as int, Fare_y=274 in example, which is not a fare value.
# Possibly Fare_y is from another column or a count.

# Since source has no Fare_y column, Fare_y must be derived from another column or aggregation.

# Let's try pivoting Fare by Embarked to get Fare_x columns, then pivot Fare by Pclass to get Fare_y columns, then merge.

# But target has Fare_x and Fare_y as single columns, not multiple columns.

# Alternative: maybe Fare_x is the mean Fare per Embarked, and Fare_y is the count of tickets per Embarked or Pclass.

# Let's try this approach:

# Pivot 1: create Fare_x = mean Fare per Embarked, join back to main table on Embarked
fare_x = df0.groupby('Embarked')['Fare'].mean().rename('Fare_x')
df = df0.merge(fare_x, on='Embarked', how='left')

# Pivot 2: create Fare_y = count of PassengerId per Pclass (integer), join back on Pclass
fare_y = df0.groupby('Pclass')['PassengerId'].count().rename('Fare_y')
df = df.merge(fare_y, on='Pclass', how='left')

# Ensure Fare_y is integer type
df['Fare_y'] = df['Fare_y'].astype('Int64')

# Reorder columns to match target schema
target_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
df = df[target_cols]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)