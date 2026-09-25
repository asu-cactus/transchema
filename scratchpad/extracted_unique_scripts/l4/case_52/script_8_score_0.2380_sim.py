import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv", index_col=0)

df = pd.concat([src0, src1, src2, src3], ignore_index=True, sort=False)

df['IsInitiator'] = df['IsInitiator'].astype('Int64')
df['WarID'] = df['WarID'].astype('Int64')
df['PolityID'] = df['PolityID'].astype('Int64')
df['StartYear'] = df['StartYear'].astype('Int64')
df['StartMonth'] = df['StartMonth'].astype('Int64')
df['StartDay'] = df['StartDay'].astype('Int64')
df['EndYear'] = df['EndYear'].astype('Int64')
df['EndMonth'] = df['EndMonth'].astype('Int64')
df['EndDay'] = df['EndDay'].astype('Int64')

def side_to_int(x):
    if pd.isna(x):
        return pd.NA
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        return int(x)
    if isinstance(x, str):
        if x.isdigit():
            return int(x)
        if x.upper() == 'A':
            return 1
        if x.upper() == 'B':
            return 0
    return pd.NA

df['Side'] = df['Side'].apply(side_to_int).astype('Int64')
df['Outcome'] = df['Outcome'].astype('Int64')
df['Deaths'] = df['Deaths'].astype('Int64')

# PolityName in target schema is integer, but source has string in some sources
# We convert PolityName to integer if possible, else NaN
def polityname_to_int(x):
    try:
        return int(x)
    except:
        return pd.NA

df['PolityName'] = df['PolityName'].apply(polityname_to_int).astype('Int64')

df = df[['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)