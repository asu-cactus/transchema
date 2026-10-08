import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_1.csv", index_col=0)

df_unpivot = df0[['Department', 'Reg Count', 'Term']].copy()
df_unpivot = df_unpivot.rename(columns={'Reg Count': 'Value', 'Term': 'Term'})

df_pivot = df_unpivot.pivot_table(index='Department', columns='Term', values='Value', aggfunc='sum')

df_pivot = df_pivot.rename(columns=lambda x: str(x))
target_columns = ['20153', '20161', '20162']
for col in target_columns:
    if col not in df_pivot.columns:
        df_pivot[col] = pd.NA

df_result = df_pivot.reset_index()[['Department'] + target_columns]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length3_22/target_multisource_mcts.csv", index=False)