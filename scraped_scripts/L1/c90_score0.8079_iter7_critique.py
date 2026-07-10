import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

# Count dogs with each dog stage flag (not null)
doggo_count = df['doggo'].notna().sum()
floofer_count = df['floofer'].notna().sum()
pupper_count = df['pupper'].notna().sum()
puppo_count = df['puppo'].notna().sum()

# Count dogs with no dog stage (all four columns null)
no_dog_stage_count = df[['doggo', 'floofer', 'pupper', 'puppo']].isna().all(axis=1).sum()

# Create result DataFrame with dog_type and counts
result = pd.DataFrame({
    'dog_type': [doggo_count, floofer_count, pupper_count, puppo_count, no_dog_stage_count]
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)