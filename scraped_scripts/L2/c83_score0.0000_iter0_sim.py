import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_83/training_0.csv", index_col=0)
df0 = df0.rename(columns={'date': 'date', 'Fare': 'price'}) if 'Fare' in df0.columns else df0
if 'price' not in df0.columns and 'Fare' in df0.columns:
    df0['price'] = df0['Fare']
if 'date' not in df0.columns:
    raise ValueError("Source table does not contain 'date' column")

df = df0[['date', 'price']].copy()
df['date'] = df['date'].astype(str)
df['price'] = df['price'].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_83/target_multisource_mcts.csv", index=False)