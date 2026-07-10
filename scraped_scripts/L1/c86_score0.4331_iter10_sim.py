import pandas as pd
import re

def normalize_spaces(s):
    if pd.isna(s):
        return s
    return re.sub(r'\s+', ' ', s.strip())

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv', index_col=0)
df0['neighbourhood'] = df0['neighbourhood'].apply(normalize_spaces)
result = df0[['neighbourhood', 'price']].copy()
result.rename(columns={'price': 'price_24'}, inplace=True)
result['price_24'] = result['price_24'].astype('Int64')
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv', index=False)