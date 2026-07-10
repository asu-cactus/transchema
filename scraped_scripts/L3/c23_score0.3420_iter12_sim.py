import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_23/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_23/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_23/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_23/training_3.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

for i, df in enumerate(dfs):
    df['Year'] = 2013 + i

df_all = pd.concat(dfs, ignore_index=True)

df_melted = df_all.melt(id_vars=['Wrestler', 'Year'], value_vars=['Wins', 'Losses', 'Draws'], var_name='Result', value_name='Count')

df_pivot = df_melted.pivot_table(index='Wrestler', columns=['Year', 'Result'], values='Count', aggfunc='sum')

df_pivot.columns = [f"{year} {result}" for year, result in df_pivot.columns]

df_pivot = df_pivot.reset_index()

cols = ['Wrestler']
for year in range(2013, 2017):
    for result in ['Wins', 'Losses', 'Draws']:
        col = f"{year} {result}"
        if col not in df_pivot.columns:
            df_pivot[col] = pd.NA
        cols.append(col)

df_final = df_pivot[cols]

df_final = df_final.astype({c: 'Int64' for c in cols if c != 'Wrestler'})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_23/target_multisource_mcts.csv", index=False)