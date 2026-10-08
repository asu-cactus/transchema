import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_86/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_86/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_86/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_86/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_86/training_4.csv"
]

def clean_precio(s):
    # Convert to string
    s = s.astype(str)
    # Remove thousands separator '.' if any
    s = s.str.replace('.', '', regex=False)
    # Replace decimal separator ',' with '.'
    s = s.str.replace(',', '.', regex=False)
    # Convert to numeric, coercing errors to NaN
    return pd.to_numeric(s, errors='coerce')

dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    df['precio'] = clean_precio(df['precio'])
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts.csv", index=False)