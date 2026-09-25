import pandas as pd

# Read the single source table (if more, read and union them)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

# Compute dog_type column based on dog stage columns
df0 = df0.assign(
    dog_type=0
).assign(
    dog_type=lambda df: df['doggo'].notna().astype(int)*4471 +
                       df['floofer'].notna().astype(int)*30 +
                       df['pupper'].notna().astype(int)*8 +
                       df['puppo'].notna().astype(int)*4
)

# Since dog stages are mutually exclusive, the above sums will be >0 only for one stage.
# But if multiple stages are present, the sum would be incorrect.
# So better to assign dog_type by priority:

def assign_dog_type(row):
    if pd.notna(row['doggo']):
        return 4471
    if pd.notna(row['floofer']):
        return 30
    if pd.notna(row['pupper']):
        return 8
    if pd.notna(row['puppo']):
        return 4
    return 0

df0['dog_type'] = df0.apply(assign_dog_type, axis=1)

# Group by dog_type and count occurrences
result = df0.groupby('dog_type', as_index=False).size().rename(columns={'size': 'dog_type'})

# Output only the dog_type column (counts)
result = result[['dog_type']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)