import pandas as pd

dfs = []
for i in range(5):
    df = pd.read_csv(
        f'autopipeline-benchmarks/github-pipelines/length4_86/training_{i}.csv',
        index_col=0
    )
    df['precio'] = pd.to_numeric(df['precio'], errors='coerce').astype(float)
    df['condicion'] = df['condicion'].str.split(' - ').str[0]
    dfs.append(df)

pd.concat(dfs, ignore_index=True).to_csv(
    'autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts_recovery_test_val.csv'
)