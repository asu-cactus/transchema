import re
import pandas as pd

infile_list = [
"logs-auto-suggest-llm-len-10-per/all_similarity_scores_auto_suggest_llm_len5_target0_source100_20240916_230644.log",
"logs-auto-suggest-llm-len-10-per/all_similarity_scores_auto_suggest_llm_len5_target18_source100_20240916_232254.log",
"logs-auto-suggest-llm-len-10-per/all_similarity_scores_auto_suggest_llm_len5_target67_source100_20240917_000517.log"
]

outfile_list = ['temp_5_0_16_10_per.xlsx','temp_5_18_67_10_per.xlsx','temp_5_67_100_10_per.xlsx']

cnt_ = -1
for infile in infile_list : 
    cnt_ = cnt_+1

    pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - INFO - Started Experiment for : "
    pat = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - INFO - "

    with open(infile, 'r') as file:
        file_content = file.read()

    sections = re.split(pattern, file_content)

    tasks = dict()

    cnt  = 0
    for i in range(1,len(sections)) :
        sec = sections[i]
        # print(sec)
        task_name = sec.partition('\n')[0]
        sec = sec[sec.find('\n')+1:sec.rfind('\n')]
        # print(sections[i])
        tasks[task_name] = dict()
        
        pattern_to_diff_tasks = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - INFO - Query of Type : "

        queries = re.split(pattern_to_diff_tasks, sec)
        # print(queries)
        for j in range(1,len(queries)) :
            q = queries[j]
            op_name = q.partition('\n')[0]
            # print(op_name)
            tasks[task_name][op_name] = dict()
            q = q[q.find('\n')+1:q.rfind('\n')]
            logs_query = re.split(pat, q)
            for l in logs_query : 
                if('Result Recieved : ' in l) :
                    res = l.split(':')[1].strip().strip('$')
                    tasks[task_name][op_name]["result"] = res
                if('Cost of the query : ' in l) :
                    res = eval(l.split(": ", 1)[1])
                    # print(res)
                    tasks[task_name][op_name]["cost_dict"] = res
                if('Time taken for this prompt : ' in l) :
                    res = float(l.split(": ")[1].strip())
                    tasks[task_name][op_name]["time_taken"] = res

        #Get answers if the task was successful and overall summary
        
        final_results = re.split(pat, queries[-1]) 
        for f in final_results : 
            if(str('Task : ' + task_name) in f) :
                acc = float(f.split("Accuracy : ")[1].split(",")[0].strip())
                is_correct = (f.split("is_correct : ")[1].split(",")[0].strip() == "True")
                tasks[task_name]["accuracy"] = acc
                tasks[task_name]["is_correct"] = is_correct
            if(str('Task Summary') in f) :
                tq = int(f.split("Total queries made during this task : ")[1].split("\n")[0].strip())
                cs = eval(f.split("Cost summary : ")[1].split("\n")[0].strip())
                op_history = eval(f.split("Tasks Used : ")[1].split("\n")[0].strip())
                time = float(f.split("Time elapsed : ")[1].split("\n")[0].strip())
                tasks[task_name]["total_queries"] = tq
                tasks[task_name]["cost_summary"] = cs
                tasks[task_name]["operation_history"] = op_history
                tasks[task_name]['time_taken'] = time 
    # print(tasks)

    #Create Dataframe for each target
    data = []

    #format [name, is_correct, accuracy, total_cost, total_time, history, queries_used]
    for k in tasks.keys() :
        d = [k]
        if('is_correct' in tasks[k].keys()) :
            d.append(tasks[k]["is_correct"])
        else : d.append(0)

        if('accuracy' in tasks[k].keys()) :
            d.append(tasks[k]["accuracy"])
        else : d.append(0)

        if('cost_summary' in tasks[k].keys()) :
            d.append(tasks[k]["cost_summary"]["total_cost"])
        else : d.append(0)

        if('time_taken' in tasks[k].keys()) : 
            d.append(tasks[k]["time_taken"])
        else : d.append(0) 

        if('operation_history' in tasks[k].keys()) :
            d.append(tasks[k]["operation_history"])
        else : d.append("0")

        if('total_queries' in tasks[k].keys()) :
            d.append(tasks[k]["total_queries"])
        else : d.append("0")

        data.append(d)

    df = pd.DataFrame(data, columns=['task_name', 'is_correct', 'accuracy', 'total_cost', 'time_taken', 'op_history', 'total_queries'])

    df.to_excel('output_excel_present/' + outfile_list[cnt_])