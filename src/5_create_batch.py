from emojinames import get_name
from glob import glob
from pydantic import BaseModel, Field, ConfigDict
from tqdm import tqdm
import base64
import json
import os
import sys

triplets = sys.argv[1] # Output folder from 4_extract_pairs.py
jsonl_path = sys.argv[2] # Output path

class InstructionFormat(BaseModel):
  model_config = ConfigDict(extra='forbid')
  instruction: str = Field(description="Edit instruction")

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

with open(jsonl_path, "w") as f:
  for folder in tqdm(glob(os.path.join(triplets, "*"))):
    with open(os.path.join(folder, "metadata.json")) as js:
      metadata = json.loads(js.read())
      caption_before = get_name(metadata["before"])
      caption_after = get_name(metadata["after"])
    img_before = encode_image(os.path.join(folder, "before.png"))
    img_after = encode_image(os.path.join(folder, "after.png"))

    jsonl = {
      "custom_id": folder.split("/")[-1],
      "method": "POST",
      "url": "/v1/chat/completions",
      "body": {
        "model": "gpt-4o-2024-08-06",
        "messages": [
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": f'The first image is an emoji of \"{caption_before}\" and the second is an emoji of \"{caption_after}.\" Describe how the first image should be edited to look like the second image. Do not just say \"Change to match the second image/emoji,\" but specify the the expected result. Also, make the instruction as clear and as short as possible.\n\nFor example, if a plane is landing towards the runway in the first image and taking off in the second, you could say \"Make the plane take off.\"',
              },{
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/png;base64,{img_before}"
                }
              },{
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/png;base64,{img_after}"
                }
              }
            ]
          }
        ],
        "response_format": {
          "type": "json_schema",
          "json_schema": {
            "name": "instruction",
            "schema": InstructionFormat.model_json_schema(),
            "strict": True
          },
        },
      }
    }
    f.write(json.dumps(jsonl) + "\n")