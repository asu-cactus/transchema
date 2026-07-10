import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)

df_grouped = df.groupby('user_id', as_index=False).agg({
    'sad.depressed': 'mean',
    'open.stressed': 'mean'
})

df_grouped = df_grouped.rename(columns={
    'sad.depressed': 'sad',
    'open.stressed': 'stressed'
})

df_grouped['user_id'] = df_grouped['user_id'].astype(int)
df_grouped['sad'] = df_grouped['sad'].astype(float)
df_grouped['stressed'] = df_grouped['stressed'].astype(float)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)