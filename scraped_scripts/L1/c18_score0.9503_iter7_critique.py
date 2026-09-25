import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

# Group by 'y' and count the number of rows per group
count_df = df0.groupby('y').size().reset_index(name='count')

# Create the final dataframe with the target schema columns
# Assign the count value to all columns except 'y'
result_df = pd.DataFrame()
result_df['y'] = count_df['y'].astype('int64')
for col in ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']:
    result_df[col] = count_df['count'].astype('int64')

result_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)