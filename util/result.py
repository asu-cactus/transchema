import re

import pandas as pd


def calculate_avg_execution_time_and_total_cost(log_file_path):
    data = []
    total_costs = []
    successful_cases = 0
    total_cases = 0
    failed_targets = []

    with open(log_file_path, 'r') as file:
        for line in file:
            total_cases += 1
            target_name = re.search(r"^(Target\d+_\d+)", line).group(1) if re.search(r"^(Target\d+_\d+)",
                                                                                     line) else None
            success = "Successful" in line
            if not success and target_name:
                failed_targets.append(target_name)
            if success and target_name:
                successful_cases += 1
            # Extracting various time components
            gen_prompt_time = re.search(r'Generating Prompt time:(\d+\.\d+)', line)
            gpt_reaction_time = re.search(r'GPT Reaction time:(\d+\.\d+)', line)
            sql_execution_time = re.search(r'SQL Execution time:(\d+\.\d+)', line)
            cost = re.search(r"'total_cost': (\d+\.\d+)", line)

            case_data = {
                "Target Name": target_name,
                "Successful": success,
                "Generating Prompt Time": float(gen_prompt_time.group(1)) if gen_prompt_time else None,
                "GPT Reaction Time": float(gpt_reaction_time.group(1)) if gpt_reaction_time else None,
                "SQL Execution Time": float(sql_execution_time.group(1)) if sql_execution_time else None,
                "Total Cost": float(cost.group(1)) if cost else None
            }
            data.append(case_data)
            if cost:
                total_costs.append(case_data["Total Cost"])

    df = pd.DataFrame(data)
    df.to_excel("execution_summary.xlsx", index=False)

    avg_gen_prompt_time = df["Generating Prompt Time"].mean()
    avg_gpt_reaction_time = df["GPT Reaction Time"].mean()
    avg_sql_execution_time = df["SQL Execution Time"].mean()
    avg_total_cost = df["Total Cost"].mean()
    accuracy = (successful_cases / total_cases) * 100 if total_cases > 0 else 0

    return avg_gen_prompt_time, avg_gpt_reaction_time, avg_sql_execution_time, avg_total_cost, accuracy, failed_targets


def main():
    log_file_path = 'D:/transchema/log/summary_l4.log'
    avg_gen_prompt_time, avg_gpt_reaction_time, avg_sql_execution_time, avg_total_cost, accuracy, failed_targets = calculate_avg_execution_time_and_total_cost(
        log_file_path)
    print(f"Average Generating Prompt Time: {avg_gen_prompt_time}")
    print(f"Average GPT Reaction Time: {avg_gpt_reaction_time}")
    print(f"Average SQL Execution Time: {avg_sql_execution_time}")
    print(f"Average Total Cost: {avg_total_cost}")
    print(f"Accuracy: {accuracy}%")
    print("Failed Targets:")
    print(failed_targets)


if __name__ == "__main__":
    main()