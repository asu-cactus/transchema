import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

# Identify rows where any dog stage column is non-null
dog_stage_cols = ['doggo', 'floofer', 'pupper', 'puppo']
has_dog_type = df[dog_stage_cols].notna().any(axis=1)

# Count how many rows have a dog type
dog_type_count = has_dog_type.sum()

# Create result dataframe with the required schema and type
result = pd.DataFrame({'dog_type': [int(dog_type_count)]})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)