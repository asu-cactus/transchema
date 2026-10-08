import pandas as pd

source_path_0 = "autopipeline-benchmarks/github-pipelines/length2_45/training_0.csv"

df0 = pd.read_csv(source_path_0, index_col=0)

# According to the plan, first join Source2_45_0 with itself on 'Item ID'
df_joined = pd.merge(df0, df0, on='Item ID', suffixes=('_left', '_right'))

# Then union Source2_45_0 with itself (concatenate)
df_union = pd.concat([df0, df0], ignore_index=True)

# The target schema is ['Item ID': int, 'Item Name': str, 'Price': float]
# Extract these columns from the union result (which has the same schema as source)
df_result = df_union[['Item ID', 'Item Name', 'Price']].copy()

# Enforce data types
df_result['Item ID'] = df_result['Item ID'].astype(int)
df_result['Item Name'] = df_result['Item Name'].astype(str)
df_result['Price'] = df_result['Price'].astype(float)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length2_45/target_multisource_mcts.csv", index=False)