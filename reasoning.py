import os
from openai import OpenAI
import json
import openai
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time
import sys
import numpy as np
import argparse
import datetime

import utils
import example

def first_try(client, problem, options, pre_solution, first_step, amc):
    example = ""
    has_example = False
    messages = utils.construct_message(problem, pre_solution, example, options, has_example, first_step, amc)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0,
        max_tokens=5000,
        top_p=1
    )
    first_try_reasoning = response.choices[0].message.content
    print("first try for this step: " + first_try_reasoning)
    return first_try_reasoning

def answer_problem_0_shot(client, problem, options, amc):
    if amc == 12:
        prompt = "You are a professional math problem solver. I will give you a problem and four options and only one is correct. Please give the solution(fewer than 10000 tokens) to the problem in steps starting by 'Step $i$:' where $i$ is step number. And output the final choice of option in the format: '\\boxed{A}'. Only 'A,B,C,D' can be chosen and you must choose one."
    else:
        prompt = "You are a professional math problem solver. I will give you a problem and five options and only one is correct. Please give the solution(fewer than 10000 tokens) to the problem in steps starting by 'Step $i$:' where $i$ is step number. And output the final choice of option in the format: '\\boxed{A}'. Only 'A,B,C,D,E' can be chosen and you must choose one."
    messages =[
        {
            "role": "system",
            "content": prompt
        },
        {
            "role": "user",
            "content": problem
        },
        {
            "role": "user",
            "content": options
        }
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0,
        max_tokens=11000,
        top_p=1
    )
    answer = response.choices[0].message.content
    return answer


def solve(client, whole_problem, vectorizer_step, example_step_embeddings, problem2step, example_data, thrsd=0.7, amc=12):
    flag = 0
    problem = 'Problem: ' + whole_problem['question']
    options = 'Options: ' + str(whole_problem['options'])
    example_num = 0
    max_similarity = 0
    total_solution = ""
   
    #find example
    
    step_num = 0
    max_step = 20
    first_step = True
    while True:
        step_num += 1
        print(f"first try for step-{step_num}:")
        first_try_reasoning = first_try(client, problem, options, total_solution, first_step, amc)
        
        print(f"finding example step for step-{step_num}")
        has_example, example_step = example.retrieve_step(first_try_reasoning, vectorizer_step, example_step_embeddings, problem2step, example_data, thrsd)
        
        print(f"generating final step for step-{step_num}")
        new_message = utils.construct_message(problem, total_solution, example_step, options, has_example, first_step, amc)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=new_message,
            temperature=0,
            max_tokens=5000,
            top_p=1
        )
        final_reasoning = response.choices[0].message.content
        print("final reason for this step: " + final_reasoning)
        pre_solution = total_solution
        total_solution += final_reasoning
        first_step = False

        if '\\boxed' in total_solution:
            break

        if step_num > max_step or final_reasoning in pre_solution: #get stuck repeating some content, happens very occasionally
            total_solution = answer_problem_0_shot(client, problem, options, amc)
            break
    
    answer = utils.extract_answer(total_solution)
        
    return total_solution, answer

def main(args):

    thrsd = args.thrsd
    amc = args.amc
    example_file_path = args.example_file_path
    api_key = args.api_key

    client = OpenAI(
        api_key=api_key,
    )

    data=[]
    if amc == 12:
        file_path = "./AMC/AMC_12_138.jsonl"
        output_file = '1-shot-AMC=12_thrsd=0.7-new.jsonl'
    elif amc == 10:
        file_path = "./AMC/AMC_10_217.jsonl"
        output_file = '1-shot-AMC=10_thrsd=0.7.jsonl'
   
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))

    vectorizer_example_step, tfidf_matrix_example_step, example_step_embeddings, problem2step, data_example = example.construct_example_bank(example_file_path)

    for i, whole_problem in enumerate(data):
        total_solution, answer = solve(client, whole_problem, vectorizer_example_step, example_step_embeddings, problem2step, data_example, thrsd, amc)
        save = {'number': i, "solution": total_solution, "answer":answer, "gt": whole_problem['answer'], 'choice':str(whole_problem['options'])}
        print(save)
        utils.save_result(save, output_file)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Define hyper-parameters for reasoning')
    parser.add_argument('--thrsd', default=0.7, type=float, help='thrsd for filtering not similar examples')
    parser.add_argument('--amc', default=12, type=int, help='version of AMC dataset')
    parser.add_argument('--example_file_path', default="./Example/example-prm800k.jsonl", type=str, help='The file path of example problem bank')
    parser.add_argument('--api_key', default="your_api_key", type=str, help='API_KEY for OpenAI')
    args = parser.parse_args()
    
    t = str(datetime.datetime.now())
    out_file = t[2:][:-7] + '.txt'
    sys.stdout = open(out_file, 'a', buffering=30000)
    sys.stderr = open(out_file, 'a', buffering=30000)
    main(args)
    