import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

result = df.groupby('user_id', as_index=False).agg({
    'sad.depressed': 'mean',
    'open.stressed': 'mean'
})

result.columns = ['user_id', 'sad', 'stressed']

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)