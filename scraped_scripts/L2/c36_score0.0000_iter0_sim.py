import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_36/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_36/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_36/training_2.csv", index_col=0)

join_01 = pd.merge(df0, df1, on="CustomerID", how="inner")
final_df = pd.merge(join_01, df2, on="CustomerID", how="inner")

cols = ['CustomerID', 'Title', 'FirstName', 'MiddleName', 'LastName', 'Suffix', 'AddressLine1', 'AddressLine2', 'City', 
        'StateProvinceName', 'CountryRegionName', 'PostalCode', 'PhoneNumber', 'BirthDate', 'Education', 'Occupation', 
        'Gender', 'MaritalStatus', 'HomeOwnerFlag', 'NumberCarsOwned', 'NumberChildrenAtHome', 'TotalChildren', 
        'YearlyIncome', 'AveMonthSpend', 'BikeBuyer']

final_df = final_df[cols]

final_df['Suffix'] = pd.to_numeric(final_df['Suffix'], errors='coerce')
final_df['HomeOwnerFlag'] = pd.to_numeric(final_df['HomeOwnerFlag'], errors='coerce').fillna(0).astype(int)
final_df['NumberCarsOwned'] = pd.to_numeric(final_df['NumberCarsOwned'], errors='coerce').fillna(0).astype(int)
final_df['NumberChildrenAtHome'] = pd.to_numeric(final_df['NumberChildrenAtHome'], errors='coerce').fillna(0).astype(int)
final_df['TotalChildren'] = pd.to_numeric(final_df['TotalChildren'], errors='coerce').fillna(0).astype(int)
final_df['YearlyIncome'] = pd.to_numeric(final_df['YearlyIncome'], errors='coerce').fillna(0).astype(int)
final_df['AveMonthSpend'] = pd.to_numeric(final_df['AveMonthSpend'], errors='coerce').fillna(0).astype(int)
final_df['BikeBuyer'] = pd.to_numeric(final_df['BikeBuyer'], errors='coerce').fillna(0).astype(int)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_36/target_multisource_mcts.csv", index=False)