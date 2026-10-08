import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_47/training_1.csv", index_col=0)

df = pd.merge(df1, df0, on="ID", how="inner")

mapping_yes_no = {"yes": 1, "no": 0}
mapping_Mjob = {"teacher": 0, "services": 1, "at_home": 2, "health": 3, "other": 4}
mapping_Fjob = {"teacher": 0, "services": 1, "at_home": 2, "health": 3, "other": 4}
mapping_reason = {"home": 0, "reputation": 1, "course": 2, "other": 3}
mapping_guardian = {"mother": 0, "father": 1, "other": 2}
mapping_sex = {"M": 0, "F": 1}
mapping_address = {"U": 0, "R": 1}
mapping_famsize = {"LE3": 0, "GT3": 1}
mapping_Pstatus = {"T": 0, "A": 1}
mapping_schoolsup = mapping_yes_no
mapping_famsup = mapping_yes_no
mapping_paid = mapping_yes_no
mapping_activities = mapping_yes_no
mapping_nursery = mapping_yes_no
mapping_higher = mapping_yes_no
mapping_internet = mapping_yes_no
mapping_romantic = mapping_yes_no

df["sex"] = df["sex"].map(mapping_sex)
df["address"] = df["address"].map(mapping_address)
df["famsize"] = df["famsize"].map(mapping_famsize)
df["Pstatus"] = df["Pstatus"].map(mapping_Pstatus)
df["Mjob"] = df["Mjob"].map(mapping_Mjob)
df["Fjob"] = df["Fjob"].map(mapping_Fjob)
df["reason"] = df["reason"].map(mapping_reason)
df["guardian"] = df["guardian"].map(mapping_guardian)
df["schoolsup"] = df["schoolsup"].map(mapping_schoolsup)
df["famsup"] = df["famsup"].map(mapping_famsup)
df["paid"] = df["paid"].map(mapping_paid)
df["activities"] = df["activities"].map(mapping_activities)
df["nursery"] = df["nursery"].map(mapping_nursery)
df["higher"] = df["higher"].map(mapping_higher)
df["internet"] = df["internet"].map(mapping_internet)
df["romantic"] = df["romantic"].map(mapping_romantic)

df["school"] = df["school"].astype(str)

cols = ['school', 'ID', 'sex', 'age', 'address', 'famsize', 'Pstatus', 'Medu', 'Fedu', 'Mjob', 'Fjob', 'reason', 'guardian', 'traveltime', 'studytime', 'failures', 'schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher', 'internet', 'romantic', 'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health', 'absences', 'G1', 'G2', 'G3']

df = df[cols]

df = df.astype({
    'ID': 'int64',
    'sex': 'Int64',
    'age': 'Int64',
    'address': 'Int64',
    'famsize': 'Int64',
    'Pstatus': 'Int64',
    'Medu': 'Int64',
    'Fedu': 'Int64',
    'Mjob': 'Int64',
    'Fjob': 'Int64',
    'reason': 'Int64',
    'guardian': 'Int64',
    'traveltime': 'Int64',
    'studytime': 'Int64',
    'failures': 'Int64',
    'schoolsup': 'Int64',
    'famsup': 'Int64',
    'paid': 'Int64',
    'activities': 'Int64',
    'nursery': 'Int64',
    'higher': 'Int64',
    'internet': 'Int64',
    'romantic': 'Int64',
    'famrel': 'Int64',
    'freetime': 'Int64',
    'goout': 'Int64',
    'Dalc': 'Int64',
    'Walc': 'Int64',
    'health': 'Int64',
    'absences': 'Int64',
    'G1': 'int64',
    'G2': 'int64',
    'G3': 'int64'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_47/target_multisource_mcts.csv", index=False)