import json
from openai import OpenAI
import openai
import pandas as pd
import jsonlines
import json

hit = 0
total = 0
api_keys = "your_api_key"
m_name = 'gpt-4o-2024-05-13'
client = OpenAI(api_key=api_keys)
prompt = "Compare whether the given answer with the groundtruth is the same. Reply with only one single number 1 (correct) or 0 (wrong). Minor expression difference can be ignored if the two mathematical expression is the same."

i = 0
total_option = []

gt_transfer = {"A":0, "B":1, "C":2, "D":3, "E":4}

i = 0

with jsonlines.open('1-shot-AMC=12_thrsd=0.7-answer.jsonl', mode='w') as writer:
    with open('1-shot-AMC=12_thrsd=0.7.jsonl', 'r', encoding='utf-8') as file: 
        for item in jsonlines.Reader(file):
            solution = item["solution"]
            answer = item['answer']
            choice = item['choice']

            choice_list = choice.split(",")
            gt = item['gt']

            gt_answer = str(choice_list[gt_transfer[gt]])
           
            if answer == "A" or answer == "B" or answer == "C" or answer == "D" or answer == "E":
                gt_answer = gt
            
            text = "Answer: " + str(answer) +  " Groundtruth: " + str(gt_answer)

            conversation_history = [{"role": "system",
                "content": [
                    {"type": "text", "text": prompt},           
                ]
                },
                {"role": "user",
                "content": [
                    {"type": "text", "text": text},           
                ]
                } ]
            
            response = client.chat.completions.create(
                model='gpt-4o-mini-2024-07-18',
                messages = conversation_history,
                max_tokens=4096
            )
            result = response.choices[0].message.content

            save = {'number': i, "answer":answer, "gt": gt, "choice":choice, 'hit':result}
            writer.write(save)

            total += 1

            hit += int(result)

            i += 1

            #break

    print(hit)
    print(total)
    print(hit/total)