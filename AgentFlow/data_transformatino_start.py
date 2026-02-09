# Import the solver
from agentflow.agentflow.solver import construct_solver

# Set the LLM engine name
llm_engine_name = "gpt-4o"
# llm_engine_name = "dashscope" # you can use "dashscope" as well, to use the default API key in the environment variables qwen2.5-7b-instruct

# Construct the solver with only configuration operators and add_operator
solver = construct_solver(
    llm_engine_name=llm_engine_name,
    enabled_tools=[
        "Add_Operator_Tool",
        "Configure_Join_Operator_Tool",
        "Configure_Union_Operator_Tool",
        "Configure_GroupBy_Aggregate_Operator_Tool",
    ],
    tool_engine=["Default", "Default", "Default", "Default"],  # All use default engines
)

# Solve the user query
output = solver.solve(
    """1. Target Table Name: Target1_0 2. Target Schema: ['State': string, 'AverageTemperature': float] 3. Target Examples: There are 241 available target examples: State AverageTemperature 240 Zhejiang 16.185409 116 Mato Grosso 25.471903 41 Dagestan 9.737170 4. Source Information: Source 0: Source 0 Name: Source1_0_0 Source 0 Schema: ['dt', 'AverageTemperature', 'AverageTemperatureUncertainty', 'State', 'Country'] Source 0 Examples: Source 0 contains 100000 tuples, with examples as follows: dt AverageTemperature AverageTemperatureUncertainty State \ 0 2002-11-01 4.190 0.187 Rostov 1 1923-11-01 26.761 0.413 Sergipe 2 1994-09-01 25.560 0.245 Manipur Country 0 Russia 1 Brazil 2 India Source 0 File Location: autopipeline-benchmarks/github-pipelines/length1_0/test_0.csv
    """
)

# output = solver.solve(
#     """The transformation case I'm fosusing on is this :     You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what operation should be performed next?". Take this decision based on "operation history", the schema of the source, target tables, and examples in the target table.
# Allowed Operations: ['JOIN', 'UNION', 'GROUP_BY/AGGREGATE', 'PIVOT', 'UNPIVOT', 'NO_MORE_OPERATION'].
# Operation History: []

# 1. Target Table Name: Target1_85
# 2. Target Schema: ['ocd_prop_id': string, 'calaccess_prop_id': integer, 'ccdc_prop_id': integer, 'prop_name': string, 'ccdc_committee_id': integer, 'calaccess_committee_id': integer, 'committee_name_x': string, 'committee_position': string, 'committee_name_y': string, 'calaccess_filing_id': integer, 'date_received': string, 'contributor_lastname': string, 'contributor_firstname': string, 'contributor_city': string, 'contributor_state': string, 'contributor_zip': string, 'contributor_employer': string, 'contributor_occupation': string, 'contributor_is_self_employed': boolean, 'amount': float]
# 3. Target Examples: There are 56326 available target examples:                                            ocd_prop_id  calaccess_prop_id  \
# 2800  ocd-contest/cad98dde-416b-4cb3-8565-c1e8079511b3            1381268
# 699   ocd-contest/cad98dde-416b-4cb3-8565-c1e8079511b3            1381268
# 9361  ocd-contest/cad98dde-416b-4cb3-8565-c1e8079511b3            1381268

#       ccdc_prop_id                                          prop_name  \
# 2800            81  PROPOSITION 062- DEATH PENALTY. INITIATIVE STA...
# 699             81  PROPOSITION 062- DEATH PENALTY. INITIATIVE STA...
# 9361            81  PROPOSITION 062- DEATH PENALTY. INITIATIVE STA...

#       ccdc_committee_id  calaccess_committee_id  \
# 2800                446                 1302403
# 699                 446                 1302403
# 9361                446                 1302403

#                                        committee_name_x committee_position  \
# 2800  CALIFORNIA CORRECTIONAL PEACE OFFICERS ASSOCIA...             OPPOSE
# 699   CALIFORNIA CORRECTIONAL PEACE OFFICERS ASSOCIA...             OPPOSE
# 9361  CALIFORNIA CORRECTIONAL PEACE OFFICERS ASSOCIA...             OPPOSE

#                                        committee_name_y  calaccess_filing_id  \
# 2800  CALIFORNIA CORRECTIONAL PEACE OFFICERS ASSOCIA...              2013304
# 699   CALIFORNIA CORRECTIONAL PEACE OFFICERS ASSOCIA...              2013304
# 9361  CALIFORNIA CORRECTIONAL PEACE OFFICERS ASSOCIA...              2013304

#      date_received contributor_lastname contributor_firstname  \
# 2800    2015-12-16              SPANGLE              DONALD L
# 699     2015-12-16                PAIGE               DAVID L
# 9361    2015-12-16       CASAREZ CHAVEZ              RACHEL D

#      contributor_city contributor_state contributor_zip contributor_employer  \
# 2800  WEST SACRAMENTO                CA           95605  STATE OF CALIFORNIA
# 699   WEST SACRAMENTO                CA           95605  STATE OF CALIFORNIA
# 9361  WEST SACRAMENTO                CA           95605  STATE OF CALIFORNIA

#      contributor_occupation  contributor_is_self_employed  amount
# 2800   CORRECTIONAL OFFICER                         False  287.08
# 699    CORRECTIONAL OFFICER                         False  287.08
# 9361   CORRECTIONAL OFFICER                         False  287.08
# 4. Source Information:
# 	Source 0:
# 	Source 0 Name: Source1_85_0
# 	Source 0 Schema: ['calaccess_committee_id', 'committee_name', 'calaccess_filing_id', 'date_received', 'contributor_lastname', 'contributor_firstname', 'contributor_city', 'contributor_state', 'contributor_zip', 'contributor_employer', 'contributor_occupation', 'contributor_is_self_employed', 'amount']
# 	Source 0 Examples: 	 Source 0 contains 28189 tuples, with examples as follows:
#    calaccess_committee_id                              committee_name  \
# 0                 1386560  ADULT USE CAMPAIGN FOR PROPOSITION 64; THE
# 1                 1386560  ADULT USE CAMPAIGN FOR PROPOSITION 64; THE
# 2                 1386560  ADULT USE CAMPAIGN FOR PROPOSITION 64; THE

#    calaccess_filing_id date_received contributor_lastname  \
# 0              2083796    2016-09-18              BERGMAN
# 1              2083796    2016-09-18                KAHLE
# 2              2083796    2016-07-15             MCDEVITT

#   contributor_firstname contributor_city contributor_state contributor_zip  \
# 0              GRETCHEN    SPRING VALLEY                CA           91978
# 1                 MYRNA        SAN DIEGO                CA           92109
# 2                   LEO        ESCONDIDO                CA           92025

#        contributor_employer contributor_occupation  \
# 0                A NEW PATH     EXECUTIVE DIRECTOR
# 1  NATIONAL SCHOOL DISTRICT                TEACHER
# 2             LIFE IONIZERS    SEO/CONTENT MANAGER

#    contributor_is_self_employed  amount
# 0                         False    84.0
# 1                         False    35.0
# 2                         False   198.0
# 	Source 0 File Location: autopipeline-benchmarks/github-pipelines/length1_85/test_0.csv
# 	Source 1:
# 	Source 1 Name: Source1_85_1
# 	Source 1 Schema: ['ocd_prop_id', 'calaccess_prop_id', 'ccdc_prop_id', 'prop_name', 'ccdc_committee_id', 'calaccess_committee_id', 'committee_name', 'committee_position']
# 	Source 1 Examples: 	 Source 1 contains 102 tuples, with examples as follows:
#                                         ocd_prop_id  calaccess_prop_id  \
# 0  ocd-contest/b51dc64d-3562-4913-a190-69f5088c22a6            1376258
# 1  ocd-contest/b51dc64d-3562-4913-a190-69f5088c22a6            1376258
# 2  ocd-contest/b51dc64d-3562-4913-a190-69f5088c22a6            1376258

#    ccdc_prop_id                                          prop_name  \
# 0            70  PROPOSITION 051 - SCHOOL BONDS. FUNDING FOR K-...
# 1            70  PROPOSITION 051 - SCHOOL BONDS. FUNDING FOR K-...
# 2            70  PROPOSITION 051 - SCHOOL BONDS. FUNDING FOR K-...

#    ccdc_committee_id  calaccess_committee_id  \
# 0                382                 1374469
# 1                383                 1220380
# 2                384                 1282321

#                                       committee_name committee_position
# 0  YES ON PROPOSITION 51 - CALIFORNIANS FOR QUALI...            SUPPORT
# 1  COMMUNITY COLLEGE FACILITY COALITION ISSUES CO...            SUPPORT
# 2  TORLAKSON'S INVEST IN CALIFORNIA A BALLOT MEAS...            SUPPORT
# 	Source 1 File Location: autopipeline-benchmarks/github-pipelines/length1_85/test_1.csv

#     At each step of add one operator and end the task when you have all the operators and configuration needed to perform the transformation.
#     """
# )
print(output["direct_output"])
