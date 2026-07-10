import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_62/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_62/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_62/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_62/training_3.csv"
]

dfs = []
for i, path in enumerate(paths):
    df = pd.read_csv(path, index_col=0)
    year = 2013 + i
    df = df.copy()
    df['Year'] = year
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

df_melted = df_all.melt(id_vars=['Wrestler', 'Year'], value_vars=['Wins', 'Losses', 'Draws'],
                        var_name='Result', value_name='Count')

df_melted['Year_Result'] = df_melted['Year'].astype(str) + ' ' + df_melted['Result']

df_pivot = df_melted.pivot_table(index='Wrestler', columns='Year_Result', values='Count', aggfunc='sum')

df_pivot = df_pivot.reset_index()

expected_cols = ['Wrestler']
for y in range(2013, 2017):
    for r in ['Wins', 'Losses', 'Draws']:
        expected_cols.append(f"{y} {r}")

for col in expected_cols[1:]:
    if col not in df_pivot.columns:
        df_pivot[col] = 0

df_pivot = df_pivot[expected_cols]

df_pivot = df_pivot.rename(columns=lambda x: x.replace(' ', ' '))

df_pivot = df_pivot.astype({col: 'Int64' for col in expected_cols[1:]})

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_62/target_multisource_mcts.csv", index=False)