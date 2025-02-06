import json
import os
import shutil
import sys

data_folder = sys.argv[1]
OUT_PATH = "triplets"

with open("assets/dataset.json") as f:
  data = json.loads(f.read())

os.makedirs(OUT_PATH)
for item in data:
  ITEM_PATH = os.path.join(OUT_PATH, f"{item['id']:04}")
  os.makedirs(ITEM_PATH)
  shutil.copy(os.path.join(data_folder, item["after"]), os.path.join(ITEM_PATH, "after.png"))
  shutil.copy(os.path.join(data_folder, item["after"].replace(".png", ".svg")), os.path.join(ITEM_PATH, "after.svg"))
  shutil.copy(os.path.join(data_folder, item["before"]), os.path.join(ITEM_PATH, "before.png"))
  shutil.copy(os.path.join(data_folder, item["before"].replace(".png", ".svg")), os.path.join(ITEM_PATH, "before.svg"))

  with open(os.path.join(ITEM_PATH, "instruction.txt"), "w") as f:
    f.write(item["instruction"])
  with open(os.path.join(ITEM_PATH, "metadata.json"), "w") as f:
    f.write(json.dumps({
      "after": item["after"],
      "before": item["before"],
      "distance": item["distance"]
    }))