import json
import os
import sys

triplets = sys.argv[1] # Output folder from 4_extract_pairs.py
batch_output = sys.argv[2] # Output from OpenAI API

with open(batch_output) as f:
  for line in f:
    jsonl = json.loads(line)
    custom_id = jsonl["custom_id"]
    if jsonl["response"]["body"]["choices"][0]["message"]["refusal"]:
      print(f"Refused: {custom_id}")
      continue
    instruction = jsonl["response"]["body"]["choices"][0]["message"]["content"]
    with open(os.path.join(triplets, custom_id, "instruction.txt"), "w") as out:
      instruction_json = json.loads(instruction)
      out.write(instruction_json["instruction"])