import os
import json
import sys
import numpy as np
import argparse

def extract_answer(response):
    position = response.find('\\boxed{')
    if position==-1:
        return 'wrong'
    num = 1
    position += 7
    start = position
    while num>0:
        if response[position]=='{':
            num+=1
        elif response[position]=='}':
            num-=1
        position+=1
    answer_extracted = response[start:position-1]
    return answer_extracted


def construct_message(problem, solution, example, options, has_example, first_step, amc=12):
    if has_example:
        if amc==12:
            if first_step:
                prompt = "You are a professional math problem solver. I will give you a math problem and several options. And I will give you another one with its first step which you can refer to. Please output only the first step(fewer than 4000 tokens) to the first problem, starting with 'Step 1:'."
            else:
                prompt = "You are a professional math problem solver. I will give you a math problem and part of its solution. And you need to only output the next step of the solution(fewer than 4000 tokens), starting with 'Step $i$:', where $i$ is the step number. In case you don't know how to derive the correct content, an example with 'Key Step' will be given. You need to learn how 'Key Step' is derived, and implement similar strategy in your derivation procedure. If you think that the final step is derived, choose an option in the 4 options given. Output the final choice of option in the format: '\\boxed{A}'. Only 'A,B,C,D' can be chosen."
        else:
            if first_step:
                prompt = "You are a professional math problem solver. I will give you a math problem and several options. And I will give you another one with its first step which you can refer to. Please output only the first step(fewer than 4000 tokens) to the first problem, starting with 'Step 1:'."
            else:
                prompt = "You are a professional math problem solver. I will give you a math problem and part of its solution. And you need to only output the next step of the solution(fewer than 4000 tokens), starting with 'Step $i$:', where $i$ is the step number. In case you don't know how to derive the correct content, an example with 'Key Step' will be given. You need to learn how 'Key Step' is derived, and implement similar strategy in your derivation procedure. If you think that the final step is derived, choose an option in the 5 options given. Output the final choice of option in the format: '\\boxed{A}'. Only 'A,B,C,D,E' can be chosen."
        messages = [
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
            },
            {
                "role":"user",
                "content": solution
            },
            {
                "role": "user",
                "content": example
            },
        ]
    else:
        if amc == 12:
            if first_step:
                prompt = "You are a professional math problem solver. I will give you a math problem and several options. Please output only the first step(fewer than 4000 tokens) to the first problem, starting with 'Step 1:'."
            else:
                prompt = "You are a professional math problem solver. I will give you a math problem and part of its solution. And you need to output only the next step of the solution(fewer than 4000 tokens), starting with 'Step $i$:', where $i$ is the step number. If you think that the final step is derived, choose an option in the 4 options given. Output the final choice of option in the format: '\\boxed{A}'. Only 'A,B,C,D' can be chosen."
        else:
            if first_step:
                prompt = "You are a professional math problem solver. I will give you a math problem and several options. Please output only the first step(fewer than 4000 tokens) to the first problem, starting with 'Step 1:'."
            else:
                prompt = "You are a professional math problem solver. I will give you a math problem and part of its solution. And you need to output only the next step of the solution(fewer than 4000 tokens), starting with 'Step $i$:', where $i$ is the step number. If you think that the final step is derived, choose an option in the 5 options given. Output the final choice of option in the format: '\\boxed{A}'. Only 'A,B,C,D,E' can be chosen."
        messages = [
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
            },
            {
                "role":"user",
                "content":solution
            }
        ]
    return messages

def save_result(result, output_file):
    with open(output_file, 'a') as f:
        json_str = json.dumps(result)
        f.write(json_str + '\n')