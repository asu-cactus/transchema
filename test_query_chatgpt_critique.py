from llm.llm_models import TokenUsageTracker,LLMClient
from auto_suggest_llm_util import create_logger,execute_python,get_filtered_functional_dependency, get_fd_hints
from util.utils import get_test_info
import pandas as pd 
import re

json_file_path = "data/chatgpt_github_ss.json"
file_path = "query.txt"
with open(file_path, mode='r') as f:
    query = f.read()

log_dir = "log_dir_critique_with_fd_16_oct"
len_id = 1
target_id = 9
max_target_id = 9
main_folder = "autopipeline-benchmarks/github-pipelines"
fd = 1

len_idx_target_idx = str(len_id) + '_' + str(target_id)

token_tracker = TokenUsageTracker()
logger = create_logger(log_dir,len_id, target_id,max_target_id)

llm_client = LLMClient(
                model="gpt-4-turbo", tracker = token_tracker, logger = logger
        )
  
# get schema
(target_data_name, target_data_schema, target_samples, file_count, source_data_name_list,
                source_data_schema_list, source_samples_list) = (
                get_test_info(json_file_path, len_idx_target_idx, main_folder))


# get target examples
ground_truth_location = '{main_folder}/length{len_idx_target_idx}/target.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
df_ground_truth = pd.read_csv(ground_truth_location,low_memory=False)
df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)
df_ground_truth_fd = df_ground_truth.sample(n = min(10,df_ground_truth.shape[0]), replace = False)
target_samples = df_ground_truth_fd.values.tolist()
target_samples = str(target_samples)
# print(target_samples)
target_samples = target_samples.replace(' ,' , ' , ')
target_samples = target_samples.replace('],' , '],\n')

query = query.replace('$SCHEMA$', target_data_schema)
query = query.replace('$EXAMPLES$',target_samples)
if(fd == 1) :
    df_ground_truth_fd = df_ground_truth.sample(n = min(1000,df_ground_truth.shape[0]), replace = False)
    df_ground_truth_fd = df_ground_truth_fd.iloc[:, : 15]
    key,fd__ = get_filtered_functional_dependency(df_ground_truth_fd)
    # fd_hints = get_fd_hints(key,fd__)
    fd_hints = "Keys : " + str(key) + "\n"
    fd_hints += "Functional Dependencies : " + str(fd__)
    query = query.replace('$FD_HINT$', fd_hints)
    
# print(query)

res = llm_client.gpt(query)

logger.info(query)
logger.info(res[0])
logger.info(token_tracker.cost_summary())

# print(res[0])

with open(main_folder + '/length'+len_idx_target_idx+'/python_recovered.py', mode='r') as f:
    python_code = f.read()
target_location_critique = main_folder + '/length'+len_idx_target_idx+'/target_multisource_critique_refined_with_fds.csv'

query_generator = '''Based on the Critisizer Response, can you add the response in the python code.
Note : - Make sure to write the final output of the python code to {target_location_critique}
- Make sure to write the python code in-between "```Python" and "```"
- Please keep the final output columns the same as it was in the python script given.
- You just need to apply the group by according to the criticizer response.
- Do not use assignment operation for any column.
Python Code : ```Python 
{python_code}
```

Criticizer Response : ```
{res}
```
'''.format(python_code = python_code, target_location_critique = target_location_critique, res = res)

res_gen = llm_client.gpt(query_generator)

pattern = re.compile(r"```Python(.*?)```", re.DOTALL | re.IGNORECASE)
match = pattern.search(res_gen[0])
script = match.group(1).strip()

logger.info(query_generator)
logger.info(res_gen[0])
logger.info(token_tracker.cost_summary())

# print(script)
response = execute_python(script)
logger.info(response)
