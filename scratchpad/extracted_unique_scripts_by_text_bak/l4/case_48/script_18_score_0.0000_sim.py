import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

pivot_cols = ['CcodeA', 'CcodeB', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'SideADeaths', 'SideBDeaths']
pivot_df = df.pivot_table(index=['WarNum', 'Initiator', 'Outcome'], columns=['SideA', 'SideB'], values=pivot_cols, aggfunc='first')

pivot_df.columns = ['_'.join(map(str, col)).strip() for col in pivot_df.columns.values]
pivot_df = pivot_df.reset_index()

records = []
for _, row in pivot_df.iterrows():
    warnum = row['WarNum']
    initiator = row['Initiator']
    outcome = row['Outcome']
    for col in pivot_df.columns:
        if col in ['WarNum', 'Initiator', 'Outcome']:
            continue
        parts = col.split('_')
        if len(parts) < 2:
            continue
        sideA = parts[0]
        sideB = parts[1]
        suffix = '_'.join(parts[2:])
        val = row[col]
        if pd.isna(val):
            continue
        if suffix == 'CcodeA':
            polity_id = int(val)
            polity_name = int(val)
        elif suffix == 'CcodeB':
            polity_id = int(val)
            polity_name = int(val)
        else:
            continue
        # Determine which side matches initiator to assign PolityID and PolityName
        # We only want rows where initiator matches sideA or sideB
        if initiator == sideA:
            polity_id = int(row.get(f"{sideA}_{sideB}_CcodeA", pd.NA))
            polity_name = polity_id
            start_month = row.get(f"{sideA}_{sideB}_StartMonth1", pd.NA)
            start_day = row.get(f"{sideA}_{sideB}_StartDay1", pd.NA)
            start_year = row.get(f"{sideA}_{sideB}_StartYear1", pd.NA)
            end_month = row.get(f"{sideA}_{sideB}_EndMonth1", pd.NA)
            end_day = row.get(f"{sideA}_{sideB}_EndDay1", pd.NA)
            end_year = row.get(f"{sideA}_{sideB}_EndYear1", pd.NA)
            deaths = row.get(f"{sideA}_{sideB}_SideADeaths", 0)
        elif initiator == sideB:
            polity_id = int(row.get(f"{sideA}_{sideB}_CcodeB", pd.NA))
            polity_name = polity_id
            start_month = row.get(f"{sideA}_{sideB}_StartMonth1", pd.NA)
            start_day = row.get(f"{sideA}_{sideB}_StartDay1", pd.NA)
            start_year = row.get(f"{sideA}_{sideB}_StartYear1", pd.NA)
            end_month = row.get(f"{sideA}_{sideB}_EndMonth1", pd.NA)
            end_day = row.get(f"{sideA}_{sideB}_EndDay1", pd.NA)
            end_year = row.get(f"{sideA}_{sideB}_EndYear1", pd.NA)
            deaths = row.get(f"{sideA}_{sideB}_SideBDeaths", 0)
        else:
            continue
        if pd.isna(polity_id):
            continue
        record = {
            'Initiator': initiator,
            'WarID': int(warnum),
            'PolityID': int(polity_id),
            'PolityName': int(polity_name),
            'StartMonth': int(start_month) if not pd.isna(start_month) else pd.NA,
            'StartDay': int(start_day) if not pd.isna(start_day) else pd.NA,
            'StartYear': int(start_year) if not pd.isna(start_year) else pd.NA,
            'EndMonth': int(end_month) if not pd.isna(end_month) else pd.NA,
            'EndDay': int(end_day) if not pd.isna(end_day) else pd.NA,
            'EndYear': int(end_year) if not pd.isna(end_year) else pd.NA,
            'Outcome': int(outcome),
            'Deaths': int(deaths) if not pd.isna(deaths) else 0
        }
        records.append(record)

result_df = pd.DataFrame(records)
result_df = result_df.drop_duplicates(subset=['Initiator', 'WarID', 'PolityID', 'Outcome'])

result_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)