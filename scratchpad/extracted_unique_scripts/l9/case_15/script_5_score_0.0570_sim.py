import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_15/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_15/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_15/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_15/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_15/training_5.csv", index_col=0)

df0 = df0.rename(columns={
    'AQI': 'AQI_0',
    'Number of Sites Reporting': 'Number_of_Sites_Reporting_0'
})
df1 = df1.rename(columns={
    'AQI': 'AQI_1',
    'Number of Sites Reporting': 'Number_of_Sites_Reporting_1'
})
df2 = df2.rename(columns={
    'AQI': 'AQI_2',
    'Number of Sites Reporting': 'Number_of_Sites_Reporting_2'
})
df3 = df3.rename(columns={
    'AQI': 'AQI_3',
    'Number of Sites Reporting': 'Number_of_Sites_Reporting_3'
})
df4 = df4.rename(columns={
    'AQI': 'AQI_4',
    'Number of Sites Reporting': 'Number_of_Sites_Reporting_4'
})
df5 = df5.rename(columns={
    'AQI': 'AQI_5',
    'Number of Sites Reporting': 'Number_of_Sites_Reporting_5'
})

join_01 = pd.merge(df0, df1, how='inner',
                   left_on=['State Name', 'county Name', 'Category', 'Defining Parameter', 'Defining Site', 'Year'],
                   right_on=['State Name', 'county Name', 'Category', 'Defining Parameter', 'Defining Site', 'Year'],
                   suffixes=('_0', '_1'))

join_012 = pd.merge(join_01, df2, how='inner',
                    left_on=['State Name', 'county Name', 'Category', 'Defining Parameter', 'Defining Site', 'Year'],
                    right_on=['State Name', 'county Name', 'Category', 'Defining Parameter', 'Defining Site', 'Year'])

join_0123 = pd.merge(join_012, df3, how='inner',
                     left_on=['State Name', 'county Name', 'Category', 'Defining Parameter', 'Year'],
                     right_on=['State Name', 'county Name', 'Category', 'Defining Parameter', 'Year'],
                     suffixes=('', '_3'))

join_01234 = pd.merge(join_0123, df4, how='inner',
                     left_on=['State Name', 'county Name', 'Category', 'Defining Parameter', 'Year'],
                     right_on=['State Name', 'county Name', 'Category', 'Defining Parameter', 'Year'],
                     suffixes=('', '_4'))

join_012345 = pd.merge(join_01234, df5, how='inner',
                      left_on=['State Name', 'county Name', 'Category', 'Defining Parameter', 'Defining Site', 'Year'],
                      right_on=['State Name', 'county Name', 'Category', 'Defining Parameter', 'Defining Site', 'Year'],
                      suffixes=('', '_5'))

agg = join_012345.groupby([
    'State Name', 'Year', 'Month_0', 'county Name', 'State Code_0', 'County Code_0', 'Date_0',
    'Category', 'Defining Parameter', 'Defining Site'
], dropna=False).agg({
    'AQI_0': 'mean',
    'AQI_1': 'mean',
    'AQI_2': 'mean',
    'AQI_3': 'mean',
    'AQI_4': 'mean',
    'AQI_5': 'mean',
    'Number_of_Sites_Reporting_0': 'sum',
    'Number_of_Sites_Reporting_1': 'sum',
    'Number_of_Sites_Reporting_2': 'sum',
    'Number_of_Sites_Reporting_3': 'sum',
    'Number_of_Sites_Reporting_4': 'sum',
    'Number_of_Sites_Reporting_5': 'sum'
}).reset_index()

agg['AQI'] = agg[['AQI_0', 'AQI_1', 'AQI_2', 'AQI_3', 'AQI_4', 'AQI_5']].mean(axis=1).round().astype('Int64')
agg['Number of Sites Reporting'] = agg[['Number_of_Sites_Reporting_0', 'Number_of_Sites_Reporting_1', 'Number_of_Sites_Reporting_2',
                                       'Number_of_Sites_Reporting_3', 'Number_of_Sites_Reporting_4', 'Number_of_Sites_Reporting_5']].sum().astype('Int64')

result = agg.rename(columns={
    'Month_0': 'Month',
    'State Code_0': 'State Code',
    'County Code_0': 'County Code',
    'Date_0': 'Date'
})[[
    'State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Date',
    'AQI', 'Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting'
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_15/target_multisource_mcts.csv", index=False)