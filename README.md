# Transchema

## Overview

This repository contains Python scripts designed to automate the generation of SQL/Python queries using the GPT-3.5/GPT-4.0 model from OpenAI. It also includes utility functions for database operations, file reading, logging, and similarity calculations.

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Logging](#logging)
- [Contributing](#contributing)

---

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/asu-cactus/transchema.git
    ```
2. Navigate to the project directory:
    ```bash
    cd transchema
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```  
---

## Usage

1. Create a environment variable with your OpenAI API key.
    ```
    export OPENAI_API_KEY={your_openai_api_key}
    ```
2. Pick a dataset from out benchmark: {‘Smart Building’, ‘COVID-19 & Machine Log’,Commercial dataset-1’, ‘Commercial dataset-2’} and change the ‘excel_file_path’ and ‘json_file_path’ in ‘excel2json.py’ accordingly. Here is the link for the benchmark dataset <[link](https://github.com/asu-cactus/Data_Transformation_Benchmark)>
    ````
    # Path to the Excel file
    excel_file_path = '<dataset_you_picked>.xlsx'
    
    
    # Path to save the JSON file
    json_file_path = <dataset_you_picked>.json'
    ```
3. Run the `excel2json.py` script to convert the .xlsx benchmark dataset to .json format:
    ```bash
    python excel2json.py
    ```
4. You can set the configurations in experiment_multistep.sh. Here's an example
    ```
    python3 critique_data.py \
    # ─── Experiment Scope ──────────────────────────────────────────────────────
    --len_id 5 \                             # Start directory for pipeline length (e.g. length5)  
    --max_len_id 5 \                         # End directory for pipeline length (inclusive)  
    --target_id 12 \                         # Start ID of target table  
    --max_target_id 40 \                     # End ID of target table (exclusive)  

    # ─── Sampling Configuration ────────────────────────────────────────────────
    --no-perc \                              # Use fixed number of rows instead of percentage sampling  
    --target-per 25 \                        # % of target rows to sample (only if using --is-perc)  
    --target-length 3 \                      # Fixed number of rows to sample from target table  
    --source-length 3 \                      # Number of rows to sample from each source table  

    # ─── Hint Source & Anonymization ───────────────────────────────────────────
    --hint-source v3 \                       # Hint version to use: v1_kv, v1_text, v2, or v3  
    --no-anon \                              # Disable anonymization of column names in the prompt  
    --fd-flag 0 \                            # Whether to include functional dependencies (1=yes, 0=no)  

    # ─── Hint Truncation Flags & Thresholds ────────────────────────────────────
    --join-flag 0 \                          # Whether to truncate join hints (1=yes, 0=no)  
    --join-hints-truncate \                  # Thresholds used if join-flag is 1  
        0.027387593197926163 \
        0.8763891522960383 \
        0.6923226156693141 \
        0.8946066635038473 \
        0.14038693859523377 \
        0.8007445686755367 \

    --aggregate-flag 0 \                     # Whether to truncate aggregate hints (1=yes, 0=no)  
    --aggregate-hints-truncate \             # Thresholds for aggregate hint truncation  
        0.9 0.1 0.9 0.1 0.9 0.1 0.9 0.1 0.9 0.1 \

    --hints-v3-truncates \                   # Truncation settings (as JSON) for v3 text hints  
        '{"t1":0.7,"t2":0.7,"t3":0.7,"t4":10,"t5":0.1,"t6":0.8,"t7":0.4,"t8":0.3,"t9":0.2,"t10":0.3,"t11":0.5,"t12":0.7,"t13":0.2}' \

    # ─── Critique Settings ─────────────────────────────────────────────────────
    --critique_setting metadata \            # One or more critique bases (fd, metadata, anonymization)  
    --critique_type history \                # Type of critique prompt to use: hard, soft, or history  

    # ─── Prompt & Model Configuration ──────────────────────────────────────────
    --token-limit 120000 \                   # Maximum tokens allowed in the prompt  
    --model gpt-4.1-mini \                   # LLM model to use (e.g., gpt-4.1-mini, gpt-4-turbo)  
    --intermediate_materialization \         # Enable intermediate result materialization  
    --combine_ask_and_configure \            # Merge ask + configure into single LLM prompt  
    --no_thinking \                          # Disable "thinking" step (LLM directly picks next op)  

    # ─── Logging & Experiment Metadata ─────────────────────────────────────────
    --log-dir logs-auto-suggest-llm-21-04 \  # Directory to store logs  
    --experiment-name feature_v3_2 \         # Unique name for this experiment run  
    --no_of_runs 1                           # Number of times to repeat the run for averaging  


    ```
4.  Run the run.py script to start the experiment:
    ```bash
    experiment_multistep.sh
    ```

## Testing

```pytest test.py```


## Logging

Initializes a structured logging directory system for experiment results, creating necessary directories and CSV files with predefined headers for storing different types of experimental metrics.

### Directory Structure
```text
[log_dir]/
└── [experiment_name]_[YYYYMMDD]_[HHMMSS]/
    ├── args.log               # For logging all the arguments of this experiment
    ├── logs/                  # For raw log files
    └── results/               # For processed results
        ├── multi_step.csv          # Individual multi-step results
        ├── average_multi_step.csv  # Aggregated multi-step metrics  
        ├── critique.csv            # Individual critique results
        └── average_critique.csv    # Aggregated critique metrics
```

### CSV Files Created

#### multi_step.csv
```Length, Hard Match, Soft Match, Soft Acc, Cost, Latency, Score```
#### average_multi_step.csv
```Length, Hard Match, Cost, Latency, Soft Match, Soft Acc, Cost_, Latency_```
#### critique.csv
```Length, Critique Type, Hard Match, Soft Match, Soft Acc, Cost, Latency, Score```
#### average_critique.csv
```Length, Critique Type, Hard Match, Cost, Latency, Soft Match, Soft Acc, Cost_, Latency_, max```


## Contributing

Feel free to fork the project and submit a pull request with your changes!

---


