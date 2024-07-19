import random

from datetime import datetime
import os, json, random

from pathlib import Path
from typing import Any, List
    
def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

def weighted_choice(items: List[Any], current: Any, hosts: List[Any], host_chance_factor=1):
    """
    Given a list of items and a current item, returns a randomly selected item from the list
    based on a weighted probability. The weighted probability is determined by the host chance
    factor and the number of items in the list. The host chance factor determines the
    probability of selecting the host item, and the non-host weight is the probability of
    selecting any other item.

    Parameters:
        items (List[Any]): A list of items to choose from.
        current (Any): The current item.
        host_chance_factor (float, optional): The factor to multiply the host chance by. Defaults to 1.
    Returns:
        Any: A randomly selected item from the list.
    """
    host_chance = 1 / len(items) * host_chance_factor
    assert 0 < host_chance_factor <= 1, "Host chance factor must be between 0 and 1"
    non_host_chance = (1 - 1 / len(items)*len(hosts)) / (len(items)-len(hosts))
    weights = [
        0 if item == current
        else host_chance if item in hosts
        else non_host_chance
        for n, item in enumerate(items)
    ]
    return random.choices(items, weights=weights)[0]

def strip_json_string(s: str) -> str:
    # Find the position of the first '{'
    start_pos = s.find('{')
    # Find the position of the last '}'
    end_pos = s.rfind('}')
    # Slice the string to include only the content between the first '{' and the last '}'
    if start_pos != -1 and end_pos != -1:
        return s[start_pos:end_pos + 1]
    else:
        raise ValueError("Input string does not contain valid JSON object boundaries.")
    
def prune_conversation(chat_result: List):
    conv_data = chat_result.chat_history[-1].get('content')
    json_data = strip_json_string(conv_data)
    script_json = json.loads(json_data)
    return script_json


def save_conversation(chat_result, output_dir=Path("outputs/conversations"), name:str="history"):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    # Get the current datetime string
    current_datetime_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Create the output file path
    output_file_path = os.path.join(output_dir, f'{name}_json_{current_datetime_str}.json')
    # Write the list of nested JSON objects to the file
    conv_json = prune_conversation(chat_result)
    with open(output_file_path, 'w') as output_file:
        json.dump(conv_json, output_file, indent=4, ensure_ascii=False)
    print(f"JSON list saved to {output_file_path}")
