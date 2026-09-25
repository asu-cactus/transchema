import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_4.csv", index_col=0)

j01 = pd.merge(s0, s1, on="WarID", suffixes=('_0', '_1'))
j012 = pd.merge(j01, s2, on="WarID", suffixes=('', '_2'))
j0123 = pd.merge(j012, s3, on="WarID", suffixes=('', '_3'))
j01234 = pd.merge(j0123, s4, on="WarID", suffixes=('', '_4'))

def to_int_or_nan(series):
    return pd.to_numeric(series, errors='coerce').dropna().astype(int) if series.dropna().size > 0 else series.astype('Int64')

def convert_col(col):
    if col.dtype == object:
        try:
            return col.astype(int)
        except:
            return col
    else:
        return col.astype('Int64')

df = pd.DataFrame()
df['Outcome'] = j01234['Outcome_0'].combine_first(j01234['Outcome_1']).combine_first(j01234['Outcome']).combine_first(j01234['Outcome_3']).combine_first(j01234['Outcome_4']).astype('Int64')
df['WarID'] = j01234['WarID'].astype('Int64')

def first_nonnull(*cols):
    for c in cols:
        if c.notna().any():
            return c.combine_first(pd.Series(dtype=c.dtype))
    return pd.Series(dtype='Int64')

df['PolityName'] = j01234['PolityName_0'].combine_first(j01234['PolityName_1']).combine_first(j01234['PolityName']).combine_first(j01234['PolityName_3']).combine_first(j01234['PolityName_4'])
df['StartYear'] = j01234['StartYear_0'].combine_first(j01234['StartYear_1']).combine_first(j01234['StartYear']).combine_first(j01234['StartYear_3']).combine_first(j01234['StartYear_4'])
df['StartMonth'] = j01234['StartMonth_0'].combine_first(j01234['StartMonth_1']).combine_first(j01234['StartMonth']).combine_first(j01234['StartMonth_3']).combine_first(j01234['StartMonth_4'])
df['StartDay'] = j01234['StartDay_0'].combine_first(j01234['StartDay_1']).combine_first(j01234['StartDay']).combine_first(j01234['StartDay_3']).combine_first(j01234['StartDay_4'])
df['EndYear'] = j01234['EndYear_0'].combine_first(j01234['EndYear_1']).combine_first(j01234['EndYear']).combine_first(j01234['EndYear_3']).combine_first(j01234['EndYear_4'])
df['EndMonth'] = j01234['EndMonth_0'].combine_first(j01234['EndMonth_1']).combine_first(j01234['EndMonth']).combine_first(j01234['EndMonth_3']).combine_first(j01234['EndMonth_4'])
df['EndDay'] = j01234['EndDay_0'].combine_first(j01234['EndDay_1']).combine_first(j01234['EndDay']).combine_first(j01234['EndDay_3']).combine_first(j01234['EndDay_4'])
df['Initiator'] = j01234['Initiator_0'].combine_first(j01234['Initiator_1']).combine_first(j01234['Initiator']).combine_first(j01234['Initiator_3']).combine_first(j01234['Initiator_4'])
df['Deaths'] = j01234['Deaths_0'].combine_first(j01234['Deaths_1']).combine_first(j01234['Deaths']).combine_first(j01234['Deaths_3']).combine_first(j01234['Deaths_4'])

for col in ['Outcome', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Initiator']:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce').fillna(0).astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_47/target_multisource_mcts.csv", index=False)