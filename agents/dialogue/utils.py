import random

from datetime import datetime
import os
import json

from pathlib import Path
    
def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

def weighted_choice(items, current, weight=0.5, host_chance=None, host=None):
    if host_chance is None:
        host_chance = 1 / len(items)
    non_host_weight = (1 - host_chance)
    weights = [
        weight if item == items[(items.index(current) + 1) % len(items)]
        else (non_host_weight / (len(items) - 2)) if item != host
        else host_chance
        for item in items if item != current
    ]
    choices = [item for item in items if item != current]
    return random.choices(choices, weights=weights)[0]

def save_conversation(conv_json, output_dir=Path("output/conversations")):

    os.makedirs(output_dir, exist_ok=True)
    current_datetime_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file_path = os.path.join(output_dir, f'nested_json_{current_datetime_str}.json')
    with open(output_file_path, 'w') as output_file:
        json.dump(conv_json, output_file, indent=4, ensure_ascii=False)
    print(f"JSON list saved to {output_file_path}")
