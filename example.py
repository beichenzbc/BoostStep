import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys
import numpy as np
import utils

def convert_example(question, step_num):
    if step_num == 0:
        return 'Problem: ' + question['problem'] +  '\nSolution: Step 1:' + question['Step 1']
    example = 'Problem: ' + question['problem'] + '\n'
    step_key = 'Step '+str(step_num)
    for key, value in question.items():
        if 'Step' not in key:
            continue
        if key==step_key:
            example = example + '\nKey Step: ' + key + ': ' +  value
        else:
            example = example + key + ': ' + value
    return example

def construct_example_bank(file_path="./Example/example-prm800k.jsonl"):
    id1 = 0
    id2 = 0
    data_example = []
    example_problem = []
    example_step = []
    problem2step = {} #record a map between step to problem

    with open(file_path, 'r') as file:
        for line in file:
            # change string for each line into json format
            question = json.loads(line)
            data_example.append(question)

            example_problem.append(question['problem'])
            for key in question.keys():
                if 'Step' in key:
                    example_step.append(question[key])
                    problem2step[id2] = [id1, key]
                    id2 += 1
            id1 += 1


        vectorizer_example_step = TfidfVectorizer()
        tfidf_matrix_example_step = vectorizer_example_step.fit_transform(example_step)
        example_step_embeddings = tfidf_matrix_example_step.toarray()

        return vectorizer_example_step, tfidf_matrix_example_step, example_step_embeddings, problem2step, data_example

def retrieve_step(key, vectorizer_step, example_step_embeddings, problem2step, example_data, thrsd=0.7):
    new_step_embedding = vectorizer_step.transform([key]).toarray()
    similarities = cosine_similarity(new_step_embedding, example_step_embeddings).flatten()

    max_similarity = similarities.max()
    example_num = problem2step[similarities.argmax()][0]
    example_step = problem2step[similarities.argmax()][1]

    if max_similarity >= thrsd:
        has_example =  True
        example = 'Example: ' + convert_example(example_data[example_num], int(example_step.rsplit(' ', 1)[-1]))
        print("Example for current step: " + example_step)

    else:
        has_example = False
        example = ""
        print ("No Example for this step")

    return has_example, example