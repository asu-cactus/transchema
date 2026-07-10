import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_4.csv", index_col=0)

df = pd.merge(df4, df1, on="batsman", how="inner", suffixes=('_x_4', '_y_1'))
df = pd.merge(df, df0, on="batsman", how="inner", suffixes=('', '_x_0'))
df = pd.merge(df, df2, on="batsman", how="inner", suffixes=('', '_x_2'))
df = pd.merge(df, df3, on="batsman", how="inner", suffixes=('', '_y_3'))

df.rename(columns={
    'batsman_runs_x_4': 'batsman_runs_x_4',
    'batsman_runs': 'batsman_runs_x',
    'batsman_runs_x_2': 'batsman_runs_y_6',
    'batsman_runs_y_3': 'batsman_runs_y_6',
    'batsman_runs_y_1': 'total_runs'
}, inplace=True)

# Because suffixes may cause confusion, explicitly rename columns from each source:
# df0 batsman_runs -> batsman_runs_x
df.rename(columns={'batsman_runs': 'batsman_runs_x'}, inplace=True)
# df2 batsman_runs -> batsman_runs_y_6 (6s)
df.rename(columns={'batsman_runs_x_2': 'batsman_runs_y_6'}, inplace=True)
# df3 batsman_runs -> batsman_runs_y_6 (6s) or batsman_runs_y_6? The target has batsman_runs_y_6, so assign df3.batsman_runs to batsman_runs_y_6
df.rename(columns={'batsman_runs_y_3': 'batsman_runs_y_6'}, inplace=True)
# df1 total_runs -> total_runs (already named)
# df4 batsman_runs -> batsman_runs_x_4 (4s)
df.rename(columns={'batsman_runs_x_4': 'batsman_runs_x_4'}, inplace=True)

# But the above renaming is ambiguous because suffixes overlap. Let's rename carefully:

# After merges, columns are:
# from df4: batsman, no of balls, batsman_runs, strike, total_runs (from df1)
# from df0: batsman_runs (will be named batsman_runs_x after rename)
# from df2: batsman_runs (will be named batsman_runs_y_6 after rename)
# from df3: batsman_runs (will be named batsman_runs_y_6 after rename)

# To avoid confusion, rename columns before merges:

df0 = df0.rename(columns={'batsman_runs': 'batsman_runs_x'})
df2 = df2.rename(columns={'batsman_runs': 'batsman_runs_y_6'})
df3 = df3.rename(columns={'batsman_runs': 'batsman_runs_y_6'})
df4 = df4.rename(columns={'batsman_runs': 'batsman_runs_x_4'})

df = pd.merge(df4, df1, on="batsman", how="inner")
df = pd.merge(df, df0, on="batsman", how="inner")
df = pd.merge(df, df2, on="batsman", how="inner")
df = pd.merge(df, df3, on="batsman", how="inner", suffixes=('', '_df3'))

# Now df has columns:
# batsman, no of balls, batsman_runs_x_4, strike, total_runs, batsman_runs_x, batsman_runs_y_6, batsman_runs_y_6_df3

# The target schema has batsman_runs_x, batsman_runs_y, no of balls, batsman_runs_x_4, strike, batsman_runs_y_6, total_runs

# We have two columns named batsman_runs_y_6 and batsman_runs_y_6_df3 from df2 and df3 respectively.
# The target has batsman_runs_y (integer) and batsman_runs_y_6 (integer).

# We have batsman_runs_x from df0 (batsman_runs_x)
# We have batsman_runs_x_4 from df4 (batsman_runs_x_4)
# We have batsman_runs_y_6 from df2 (batsman_runs_y_6)
# We have batsman_runs_y_6_df3 from df3 (another batsman_runs_y_6, but target only has one batsman_runs_y_6)

# The target has batsman_runs_y (integer) which is missing so far.

# The only source with total_runs is df1.

# The only source with batsman_runs_y is probably from df3 or df2.

# Since df3 and df2 both have batsman_runs, and target has batsman_runs_y and batsman_runs_y_6, likely:
# batsman_runs_y = sum of batsman_runs from df3
# batsman_runs_y_6 = batsman_runs from df2

# So rename df3.batsman_runs_y_6_df3 to batsman_runs_y

df = df.rename(columns={'batsman_runs_y_6_df3': 'batsman_runs_y'})

# Now group by batsman and aggregate sums and mean as needed

agg_df = df.groupby('batsman').agg({
    'batsman_runs_x': 'sum',
    'batsman_runs_y': 'sum',
    'no of balls': 'sum',
    'batsman_runs_x_4': 'sum',
    'strike': 'mean',
    'batsman_runs_y_6': 'sum',
    'total_runs': 'sum'
}).reset_index()

agg_df['strike'] = agg_df['strike'].astype(float)
agg_df['batsman_runs_x'] = agg_df['batsman_runs_x'].astype(int)
agg_df['batsman_runs_y'] = agg_df['batsman_runs_y'].astype(int)
agg_df['no of balls'] = agg_df['no of balls'].astype(int)
agg_df['batsman_runs_x_4'] = agg_df['batsman_runs_x_4'].astype(int)
agg_df['batsman_runs_y_6'] = agg_df['batsman_runs_y_6'].astype(int)
agg_df['total_runs'] = agg_df['total_runs'].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_35/target_multisource_mcts.csv", index=False)