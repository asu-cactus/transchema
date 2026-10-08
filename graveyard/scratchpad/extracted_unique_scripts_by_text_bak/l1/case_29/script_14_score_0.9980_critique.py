import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)

# Normalize Gender values to match target categories
df0['Gender'] = df0['Gender'].where(df0['Gender'].isin(['Female', 'Male']), other='Other / Non-Disclosed')

# Group by Gender and count Purchase ID
result = df0.groupby('Gender').size().reset_index(name='0')

result['0'] = result['0'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)