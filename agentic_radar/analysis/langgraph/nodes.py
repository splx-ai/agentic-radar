import json
import os

import openai


def get_python_files(directory):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def parse_gotos(node, graph_file_path, root_directory):

    with open(graph_file_path, "r") as f:
        code = f.read()

    system_prompt = """# Role Definition
You are an analyzer of Python functions.
Your goal is to detect if a Python function returns a specific type of object and then provide a list of all the possible values of a certain argument of that object.
You are currently looking for returning the Command object, and you need to provide a list of all the possible values of the "goto" argument of that object.

# Instructions
In the first user message you will be provided with the following information:
- the code file in which the function is used as an argument to a "add_node" method between the # Code Beginning and # Code End separators
- the path to that file between the # Code File Path Beginning and # Code File Path End separators
- the name of the function as it is passed to the "add_node" method, or the AST dump of the function as it is passed to the "add_node" method between the # Function Original Name Beginning and # Function Original Name End separators
- the fully qualified name of the function between the # Fully Qualified Name Beginning and # Fully Qualified Name End separators
- the paths to all of the available files in the directory between the # File Paths Beginning and # File Paths End separators

# Task
Your job is to look for the definition of the function in the code files and see if the function returns any Command objects.
If the function returns any Command objects you must provide a list of all the possible values of the Command object's "goto" argument. The values of the "goto" argument can only be strings, END or START.
Some functions do not return any Command objects, and in those cases you should provide an empty list.
Only focus on the single function you were assigned in the first user message.

# Response format
You must respond with a JSON containing the following fields:
1. A "need_more_information" field". This is a boolean and it should be true if you need to see the code from some of the other files in the directory in order to solve the task, and false otherwise.
2. A "file_paths" filed. This is a list of strings of the file paths of files from which you need to see the code. These can only be file paths from between the # File Paths Beginning and # File Paths End separators in the first user message. It should be an empty list if the "need_more_information" field is set to false.
3. A "goto_values" list. This should contain all the possible values of the "goto" argument of the Command objects. If the function does not return any Command objects, this should be an empty list."""

    ## TODO: make this dynamic or change the whole thing with AST static analysis if possible
    client = openai.AzureOpenAI()

    first_user_message = f"""
# Code Beginning
{code}
# Code End

# Code File Path Beginning
{graph_file_path}
# Code File Path End

# Function Original Name Beginning
{node["definition"]["original"]}
# Function Original Name End

# Fully Qualified Name Beginning
{node["definition"]["fq_name"]}
# Fully Qualified Name End

# File Paths Beginning
{get_python_files(root_directory)}
# File Paths End

"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": first_user_message},
    ]

    response = client.chat.completions.create(
        model="gpt-4o", messages=messages, response_format={"type": "json_object"}
    )

    response_json = json.loads(response.choices[0].message.content)

    need_more_information = response_json["need_more_information"]

    while need_more_information:
        new_user_message = ""
        for file_path in response_json["file_paths"]:

            with open(file_path, "r") as f:
                code = f.read()
                new_user_message += f"""
# Code Beginning
{code}
# Code End

# Code File Path Beginning
{file_path}
# Code File Path End

"""

        messages.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )
        messages.append({"role": "user", "content": new_user_message})

        response = client.chat.completions.create(
            model="gpt-4o", messages=messages, response_format={"type": "json_object"}
        )

        response_json = json.loads(response.choices[0].message.content)

        need_more_information = response_json["need_more_information"]

    return response_json["goto_values"]
