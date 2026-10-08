import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_3.csv", index_col=0)

def pivot_source(df, year):
    df = df.copy()
    df['Year'] = year
    df = df.melt(id_vars=['Wrestler', 'Year'], value_vars=['Wins', 'Losses', 'Draws'], var_name='Result', value_name='Count')
    df['Year_Result'] = df['Year'].astype(str) + ' ' + df['Result']
    df_pivot = df.pivot(index='Wrestler', columns='Year_Result', values='Count')
    return df_pivot

p0 = pivot_source(df0, 2013)
p1 = pivot_source(df1, 2014)
p2 = pivot_source(df2, 2015)
p3 = pivot_source(df3, 2016)

df_merged = p0.join(p1, how='outer', lsuffix='_2013', rsuffix='_2014')
df_merged = df_merged.join(p2, how='outer')
df_merged = df_merged.join(p3, how='outer')

df_merged.reset_index(inplace=True)

# Ensure all columns in target schema exist, fill missing with 0 and convert to int
target_columns = ['Wrestler',
                  '2013 Wins', '2013 Losses', '2013 Draws',
                  '2014 Wins', '2014 Losses', '2014 Draws',
                  '2015 Wins', '2015 Losses', '2015 Draws',
                  '2016 Wins', '2016 Losses', '2016 Draws']

for col in target_columns[1:]:
    if col not in df_merged.columns:
        df_merged[col] = 0

df_merged = df_merged[target_columns]
df_merged.fillna(0, inplace=True)
for col in target_columns[1:]:
    df_merged[col] = df_merged[col].astype(int)

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_63/target_multisource_mcts.csv", index=False)