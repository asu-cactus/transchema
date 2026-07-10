import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv", index_col=0)

df0 = df0[['Country', 'AverageTemperature']]

pivoted = df0.pivot_table(index='Country', columns=None, values='AverageTemperature', aggfunc='mean').reset_index()

# Since the target schema has two columns AverageTemperature_x and AverageTemperature_y,
# but only one source table is given, we assume the pivot operation is to create two columns
# from the same source by some logic. The partial plan says PIVOT and GROUP_BY [Country].
# The source has only one AverageTemperature column.
# The target has AverageTemperature_x and AverageTemperature_y.
# Possibly the source data has multiple entries per country with different dt values.
# We can create two columns by splitting the data by some criteria.
# But since only one source is given, and no other source, we must create two columns from the same data.
# The best guess is to create AverageTemperature_x as the mean of AverageTemperature for the first half of dates,
# and AverageTemperature_y as the mean for the second half of dates per country.

df0['dt'] = pd.to_datetime(pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv", index_col=0)['dt'])

median_date = df0['dt'].median()

df_x = df0[df0['dt'] <= median_date].groupby('Country')['AverageTemperature'].mean().reset_index().rename(columns={'AverageTemperature': 'AverageTemperature_x'})
df_y = df0[df0['dt'] > median_date].groupby('Country')['AverageTemperature'].mean().reset_index().rename(columns={'AverageTemperature': 'AverageTemperature_y'})

result = pd.merge(df_x, df_y, on='Country', how='outer')

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_21/target_multisource_mcts.csv", index=False)