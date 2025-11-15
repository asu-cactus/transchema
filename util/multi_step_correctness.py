import os
import csv
import pandas as pd
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--folder', type=str, required=True, help='Folder name')

args = parser.parse_args()


def read(filename):
    with open(filename) as f:
       return(f.read())

true_count = 0

folder = args.folder

path = f"/Users/jiazou/Downloads/thing/logs-auto-suggest-llm-21-04/{folder}/results/multi_step.csv"
if os.path.exists(path):
    contents = read(path)
    contents = contents.split(',')
    for content in contents:
        if content == 'True':
            true_count += 1
    if true_count > 0:
        print(true_count)
    else:
        print("No true")
else:
    print("Path does not exist")